"""
[실제 PostgreSQL 동시성 테스트]

같은 자원에 동시에 요청이 몰릴 때 다음이 보장되는지 확인합니다.
- 재고보다 많이 팔리지 않는다 (조건부 재고 차감)
- 주문 취소가 동시에 여러 번 들어와도 재고는 한 번만 복구된다 (상태 compare-and-set)
- 같은 주문/paymentKey로 결제가 두 번 처리되지 않고, 실패 시 상태 변경도 함께 롤백된다
- 같은 리프레시 토큰으로 동시에 재발급해도 하나만 성공한다 (토큰 회전)
"""

import asyncio
import uuid

from app.lib.prisma import db as prisma
from app.services import AuthService as authService
from app.services import OrderService as orderService
from app.types.orderType import OrderCreateRequest, PaymentApproveRequest
from fastapi import HTTPException

ADDRESS = "서울시 강남구 테헤란로 1"


def _run(coro_factory):
    async def runner():
        await prisma.connect()
        cleanup: dict[str, list[int]] = {"users": [], "products": []}
        try:
            await coro_factory(cleanup)
        finally:
            if cleanup["users"]:
                await prisma.user.delete_many(where={"id": {"in": cleanup["users"]}})
            if cleanup["products"]:
                await prisma.product.delete_many(where={"id": {"in": cleanup["products"]}})
            await prisma.disconnect()

    asyncio.run(runner())


async def _create_user(cleanup) -> int:
    user = await prisma.user.create(
        data={"email": f"it-{uuid.uuid4().hex[:12]}@test.com", "name": "통합테스트", "password": "x"}
    )
    cleanup["users"].append(user.id)
    return user.id


async def _create_product(cleanup, stock: int, price: int = 1000) -> int:
    product = await prisma.product.create(
        data={"name": f"동시성 상품 {uuid.uuid4().hex[:6]}", "price": price, "stock": stock}
    )
    cleanup["products"].append(product.id)
    return product.id


async def _create_cart_item(user_id: int, product_id: int, quantity: int) -> int:
    item = await prisma.cartitem.create(data={"userId": user_id, "productId": product_id, "quantity": quantity})
    return item.id


async def _gather_outcomes(coros) -> tuple[list, list[int]]:
    results = await asyncio.gather(*coros, return_exceptions=True)
    successes = [r for r in results if not isinstance(r, BaseException)]
    errors = [r for r in results if isinstance(r, BaseException)]
    unexpected = [e for e in errors if not isinstance(e, HTTPException)]
    assert not unexpected, f"예상하지 못한 예외: {unexpected!r}"
    return successes, [e.status_code for e in errors]


def test_concurrent_orders_never_oversell():
    async def scenario(cleanup):
        stock = 3
        buyers = 10
        product_id = await _create_product(cleanup, stock=stock)
        requests = []
        for _ in range(buyers):
            user_id = await _create_user(cleanup)
            cart_item_id = await _create_cart_item(user_id, product_id, 1)
            requests.append((user_id, cart_item_id))

        successes, error_codes = await _gather_outcomes(
            orderService.createOrder(user_id, OrderCreateRequest(address=ADDRESS, cartItemIds=[cart_item_id]))
            for user_id, cart_item_id in requests
        )

        product = await prisma.product.find_unique(where={"id": product_id})
        ordered = await prisma.orderitem.count(where={"productId": product_id})
        assert len(successes) == stock
        assert product.stock == 0
        assert ordered == stock
        # 사전 확인 단계(400) 또는 트랜잭션 내 조건부 차감(409)에서 거절됩니다.
        assert set(error_codes) <= {400, 409}

    _run(scenario)


def test_failed_stock_decrement_rolls_back_whole_order():
    """두 상품 중 하나라도 재고가 부족하면, 이미 차감한 다른 상품 재고와 주문 생성까지 전부 롤백됩니다."""

    async def scenario(cleanup):
        user_id = await _create_user(cleanup)
        plenty = await _create_product(cleanup, stock=10)
        scarce = await _create_product(cleanup, stock=1)
        cart_a = await _create_cart_item(user_id, plenty, 2)
        cart_b = await _create_cart_item(user_id, scarce, 1)

        # 사전 확인은 통과한 뒤, 트랜잭션 직전에 다른 주문이 scarce 재고를 가져간 상황을 만듭니다.
        original_create = orderService.orderRepository.createOrderWithItems

        async def steal_then_create(**kwargs):
            await prisma.product.update(where={"id": scarce}, data={"stock": 0})
            return await original_create(**kwargs)

        orderService.orderRepository.createOrderWithItems = steal_then_create
        try:
            successes, error_codes = await _gather_outcomes(
                [orderService.createOrder(user_id, OrderCreateRequest(address=ADDRESS, cartItemIds=[cart_a, cart_b]))]
            )
        finally:
            orderService.orderRepository.createOrderWithItems = original_create

        assert successes == []
        assert error_codes == [409]
        assert (await prisma.product.find_unique(where={"id": plenty})).stock == 10
        assert await prisma.order.count(where={"userId": user_id}) == 0
        assert await prisma.cartitem.count(where={"userId": user_id}) == 2

    _run(scenario)


def test_concurrent_cancels_restock_only_once():
    async def scenario(cleanup):
        user_id = await _create_user(cleanup)
        product_id = await _create_product(cleanup, stock=5)
        cart_item_id = await _create_cart_item(user_id, product_id, 2)
        order = await orderService.createOrder(user_id, OrderCreateRequest(address=ADDRESS, cartItemIds=[cart_item_id]))
        assert (await prisma.product.find_unique(where={"id": product_id})).stock == 3

        successes, error_codes = await _gather_outcomes(
            orderService.cancelOrder(user_id, order["id"]) for _ in range(8)
        )

        assert len(successes) == 1
        assert set(error_codes) <= {400, 409}
        assert (await prisma.product.find_unique(where={"id": product_id})).stock == 5

    _run(scenario)


def test_concurrent_payment_approvals_are_idempotent_and_atomic():
    async def scenario(cleanup):
        user_id = await _create_user(cleanup)
        product_id = await _create_product(cleanup, stock=10, price=5000)
        cart_1 = await _create_cart_item(user_id, product_id, 1)
        order = await orderService.createOrder(user_id, OrderCreateRequest(address=ADDRESS, cartItemIds=[cart_1]))
        payment_key = f"pk_{uuid.uuid4().hex}"
        body = PaymentApproveRequest(orderId=order["id"], paymentKey=payment_key, amount=5000, method="CARD")

        successes, error_codes = await _gather_outcomes(orderService.approvePayment(user_id, body) for _ in range(6))

        assert len(successes) == 1
        assert set(error_codes) <= {400, 409}
        assert await prisma.payment.count(where={"orderId": order["id"]}) == 1
        assert (await prisma.order.find_unique(where={"id": order["id"]})).status == "PAID"

        # 같은 paymentKey를 다른 주문에 재사용 → 유니크 제약으로 거절되고, 주문 상태 변경도 롤백되어야 합니다.
        cart_2 = await _create_cart_item(user_id, product_id, 1)
        order_2 = await orderService.createOrder(user_id, OrderCreateRequest(address=ADDRESS, cartItemIds=[cart_2]))
        reuse = PaymentApproveRequest(orderId=order_2["id"], paymentKey=payment_key, amount=5000, method="CARD")
        _, codes = await _gather_outcomes([orderService.approvePayment(user_id, reuse)])

        assert codes == [409]
        assert (await prisma.order.find_unique(where={"id": order_2["id"]})).status == "PENDING"
        assert await prisma.payment.count(where={"orderId": order_2["id"]}) == 0

    _run(scenario)


def test_concurrent_refresh_with_same_token_rotates_once():
    async def scenario(cleanup):
        user_id = await _create_user(cleanup)
        tokens = await authService.login({"id": user_id})

        successes, error_codes = await _gather_outcomes(
            authService.refreshToken(tokens["refreshToken"]) for _ in range(5)
        )

        assert len(successes) == 1
        assert set(error_codes) == {401}

        # 로그아웃하면 회전으로 받은 새 토큰도 더 이상 쓸 수 없습니다.
        await authService.logout(user_id)
        _, codes = await _gather_outcomes([authService.refreshToken(successes[0]["refreshToken"])])
        assert codes == [401]
        assert await prisma.refreshtoken.count(where={"userId": user_id, "revokedAt": None}) == 0

    _run(scenario)
