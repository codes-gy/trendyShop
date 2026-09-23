from datetime import UTC, datetime
from typing import Any

from app.lib.prisma import db as prisma

_INCLUDE_FULL = {
    "orderItems": True,
    "payment": True,
    "deliveries": True,
}


async def findManyByUser(user_id: int) -> list[dict[str, Any]]:
    """
    [내 주문 목록 조회] (주문 상품/결제/배송 정보 포함)
    """
    orders = await prisma.order.find_many(
        where={"userId": user_id},
        include=_INCLUDE_FULL,
        order={"createdAt": "desc"},
    )
    return [order.model_dump() for order in orders]


async def findById(order_id: int) -> dict[str, Any] | None:
    """
    [주문 단건 상세 조회] (소유자 검증은 서비스 레이어에서 처리)
    """
    order = await prisma.order.find_unique(
        where={"id": order_id},
        include=_INCLUDE_FULL,
    )
    return order.model_dump() if order else None


async def createOrderWithItems(
    user_id: int,
    address: str,
    total_price: int,
    order_items: list[dict[str, Any]],
    cart_item_ids: list[int],
) -> dict[str, Any]:
    """
    [주문 생성 트랜잭션]
    - Order + OrderItem 스냅샷 생성, 주문된 상품들의 재고 차감, 체크아웃에 쓰인
      장바구니 아이템 삭제를 하나의 트랜잭션으로 묶어 원자적으로 처리합니다.
      (중간에 하나라도 실패하면 전체가 롤백됩니다.)
    """
    async with prisma.tx() as transaction:
        new_order = await transaction.order.create(
            data={
                "userId": user_id,
                "address": address,
                "totalPrice": total_price,
                "orderItems": {"create": order_items},
            },
            include=_INCLUDE_FULL,
        )

        for item in order_items:
            await transaction.product.update(
                where={"id": item["productId"]},
                data={"stock": {"decrement": item["quantity"]}},
            )

        if cart_item_ids:
            await transaction.cartitem.delete_many(where={"id": {"in": cart_item_ids}})

    return new_order.model_dump()


async def updateStatus(order_id: int, order_status: str) -> dict[str, Any]:
    """
    [주문 상태 변경]
    """
    updated = await prisma.order.update(
        where={"id": order_id},
        data={"status": order_status},
        include=_INCLUDE_FULL,
    )
    return updated.model_dump()


async def createPayment(order_id: int, payment_key: str, method: str, amount: int) -> dict[str, Any]:
    """
    [결제 정보 생성] (Order와 1:1 관계)
    """
    payment = await prisma.payment.create(
        data={
            "orderId": order_id,
            "paymentKey": payment_key,
            "method": method,
            "amount": amount,
            "paidAt": datetime.now(UTC),
        }
    )
    return payment.model_dump()


async def hasPurchasedProduct(user_id: int, product_id: int) -> bool:
    """
    [해당 유저가 이 상품을 구매(결제 완료 이상)한 이력이 있는지 확인]
    - 리뷰 작성 자격 검증에 사용됩니다. (PENDING/CANCELLED 주문은 인정하지 않습니다.)
    """
    order_item = await prisma.orderitem.find_first(
        where={
            "productId": product_id,
            "order": {
                "is": {
                    "userId": user_id,
                    "status": {"in": ["PAID", "SHIPPED", "DELIVERED"]},
                }
            },
        }
    )
    return order_item is not None


async def cancelOrderWithRestock(order_id: int, order_items: list[dict[str, Any]]) -> dict[str, Any]:
    """
    [주문 취소 트랜잭션]
    - 각 주문 아이템 수량만큼 상품 재고를 복구하고, 주문 상태를 CANCELLED로 전환합니다.
      (재고 차감은 주문 생성 시점에 이루어지므로, PENDING/PAID 상태 모두 복구가 필요합니다.)
    """
    async with prisma.tx() as transaction:
        for item in order_items:
            await transaction.product.update(
                where={"id": item["productId"]},
                data={"stock": {"increment": item["quantity"]}},
            )

        cancelled_order = await transaction.order.update(
            where={"id": order_id},
            data={"status": "CANCELLED"},
            include=_INCLUDE_FULL,
        )

    return cancelled_order.model_dump()
