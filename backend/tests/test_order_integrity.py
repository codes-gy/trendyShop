"""
[주문/결제 정합성 회귀 테스트]

- 결제 승인: 클라이언트 값만 믿지 않고 PG 승인 API 결과를 서버에서 검증하는지
- 재고: 트랜잭션 안의 조건부 차감(stock >= 수량)으로 초과 판매를 막는지
- 취소: 상태 전이를 compare-and-set으로 처리해 재고가 두 번 복구되지 않는지
- 결제 완료 주문 취소: 환불 연동 전까지 사용자 직접 취소를 막는지

서비스/라우터 레벨 테스트는 리포지토리 함수를 monkeypatch로 대체하고,
리포지토리 레벨 테스트는 가짜 트랜잭션 객체로 Prisma 호출 인자/순서를 검증합니다.
(실제 PostgreSQL 위에서의 동시성 테스트는 tests_integration/ 에 있습니다.)
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest
from app.lib import payment as paymentLib
from app.lib.passport.index import jwt_authenticate
from app.lib.payment import FakePaymentGateway, PaymentConfirmation, PaymentGatewayError, TossPaymentGateway
from app.main import app
from app.repositories import CartRepository as cartRepository
from app.repositories import OrderRepository as orderRepository
from app.repositories import ProductRepository as productRepository
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

USER = {"id": 1, "email": "user@test.com", "role": "USER"}
ADMIN = {"id": 99, "email": "admin@test.com", "role": "ADMIN"}
PAYMENT_BODY = {"orderId": 1, "paymentKey": "pg_key_123", "amount": 20000, "method": "CARD"}


def _sample_order(**overrides) -> dict:
    base = {
        "id": 1,
        "userId": 1,
        "totalPrice": 20000,
        "status": "PENDING",
        "address": "서울시 강남구 테헤란로 1",
        "orderItems": [],
        "payment": None,
        "deliveries": [],
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }
    base.update(overrides)
    return base


async def _pending_order_20000(order_id):
    return _sample_order(id=1, userId=1, status="PENDING", totalPrice=20000)


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _as(user):
    app.dependency_overrides[jwt_authenticate] = lambda: user


class _StubGateway:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    async def confirm(self, payment_key, pg_order_id, amount):
        self.calls.append((payment_key, pg_order_id, amount))
        if self.error:
            raise self.error
        return self.result


def _forbid_mark_paid(monkeypatch):
    async def fake_mark_paid(*args, **kwargs):
        raise AssertionError("PG 승인 검증에 실패한 결제는 PAID 처리되면 안 됩니다.")

    monkeypatch.setattr(orderRepository, "markPaidWithPayment", fake_mark_paid)


# -----------------------------------------------------------------
# 결제 승인 서버 검증
# -----------------------------------------------------------------
def test_approve_payment_rejected_by_pg_is_not_marked_paid(monkeypatch):
    """클라이언트가 임의로 만든 paymentKey는 PG 승인 단계에서 거절되어 PAID가 되면 안 됩니다."""
    _as(USER)
    gateway = _StubGateway(error=PaymentGatewayError("존재하지 않는 결제입니다.", code="NOT_FOUND_PAYMENT"))
    monkeypatch.setattr(paymentLib, "getPaymentGateway", lambda: gateway)
    monkeypatch.setattr(orderRepository, "findById", _pending_order_20000)
    _forbid_mark_paid(monkeypatch)

    resp = client.post("/orders/payment", json=PAYMENT_BODY)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    # 승인 요청에는 서버에 저장된 주문 금액과 PG 주문번호 형식이 사용되어야 합니다.
    assert gateway.calls == [("pg_key_123", "trendy-order-1", 20000)]


def test_approve_payment_pg_network_error_returns_502(monkeypatch):
    _as(USER)
    gateway = _StubGateway(error=PaymentGatewayError("통신 실패", retryable=True))
    monkeypatch.setattr(paymentLib, "getPaymentGateway", lambda: gateway)
    monkeypatch.setattr(orderRepository, "findById", _pending_order_20000)
    _forbid_mark_paid(monkeypatch)

    resp = client.post("/orders/payment", json=PAYMENT_BODY)

    assert resp.status_code == status.HTTP_502_BAD_GATEWAY


@pytest.mark.parametrize(
    "confirmation",
    [
        PaymentConfirmation("pg_key_123", "trendy-order-1", 100, "DONE"),  # 승인 금액 불일치
        PaymentConfirmation("pg_key_123", "trendy-order-999", 20000, "DONE"),  # 다른 주문의 결제
        PaymentConfirmation("other_key", "trendy-order-1", 20000, "DONE"),  # 다른 paymentKey
        PaymentConfirmation("pg_key_123", "trendy-order-1", 20000, "WAITING_FOR_DEPOSIT"),  # 승인 완료 아님
    ],
)
def test_approve_payment_pg_result_mismatch_is_rejected(monkeypatch, confirmation):
    _as(USER)
    monkeypatch.setattr(paymentLib, "getPaymentGateway", lambda: _StubGateway(result=confirmation))
    monkeypatch.setattr(orderRepository, "findById", _pending_order_20000)
    _forbid_mark_paid(monkeypatch)

    resp = client.post("/orders/payment", json=PAYMENT_BODY)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_approve_payment_amount_mismatch_does_not_call_pg(monkeypatch):
    _as(USER)
    gateway = _StubGateway(error=AssertionError("금액이 다르면 PG를 호출하면 안 됩니다."))
    monkeypatch.setattr(paymentLib, "getPaymentGateway", lambda: gateway)
    monkeypatch.setattr(orderRepository, "findById", _pending_order_20000)

    resp = client.post("/orders/payment", json={**PAYMENT_BODY, "amount": 1})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert gateway.calls == []


def test_approve_payment_conflict_when_order_changed_after_pg_confirm(monkeypatch):
    """PG 승인 후 DB 반영 시점에 주문이 이미 PAID/CANCELLED로 바뀌었으면 409를 반환합니다."""
    _as(USER)
    monkeypatch.setattr(paymentLib, "getPaymentGateway", lambda: FakePaymentGateway())
    monkeypatch.setattr(orderRepository, "findById", _pending_order_20000)

    async def fake_mark_paid(*args, **kwargs):
        raise orderRepository.OrderStatusConflictError(1)

    monkeypatch.setattr(orderRepository, "markPaidWithPayment", fake_mark_paid)

    resp = client.post("/orders/payment", json=PAYMENT_BODY)

    assert resp.status_code == status.HTTP_409_CONFLICT


def test_approve_payment_duplicate_payment_key_returns_409(monkeypatch):
    """같은 paymentKey가 이미 저장되어 있으면(유니크 제약 위반) 409를 반환합니다. (멱등성)"""
    from prisma.errors import UniqueViolationError

    _as(USER)
    monkeypatch.setattr(paymentLib, "getPaymentGateway", lambda: FakePaymentGateway())
    monkeypatch.setattr(orderRepository, "findById", _pending_order_20000)

    async def fake_mark_paid(*args, **kwargs):
        raise UniqueViolationError({"user_facing_error": {"message": "Unique constraint failed"}})

    monkeypatch.setattr(orderRepository, "markPaidWithPayment", fake_mark_paid)

    resp = client.post("/orders/payment", json=PAYMENT_BODY)

    assert resp.status_code == status.HTTP_409_CONFLICT


# -----------------------------------------------------------------
# 토스페이먼츠 게이트웨이 (httpx.MockTransport로 실제 네트워크 없이 검증)
# -----------------------------------------------------------------
def test_toss_gateway_sends_confirm_request_with_basic_auth():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers["Authorization"]
        captured["idempotency"] = request.headers["Idempotency-Key"]
        captured["body"] = request.read()
        return httpx.Response(
            200,
            json={
                "paymentKey": "pg_key_123",
                "orderId": "trendy-order-1",
                "totalAmount": 20000,
                "status": "DONE",
                "method": "카드",
            },
        )

    gateway = TossPaymentGateway("test_sk_abc", "https://pg.example", transport=httpx.MockTransport(handler))
    result = asyncio.run(gateway.confirm("pg_key_123", "trendy-order-1", 20000))

    assert captured["url"] == "https://pg.example/v1/payments/confirm"
    # "test_sk_abc:" 를 base64 인코딩한 값
    assert captured["auth"] == "Basic dGVzdF9za19hYmM6"
    assert captured["idempotency"] == "pg_key_123"
    assert b'"amount":20000' in captured["body"].replace(b" ", b"")
    assert result == PaymentConfirmation("pg_key_123", "trendy-order-1", 20000, "DONE", "카드")


def test_toss_gateway_raises_on_rejection():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"code": "NOT_FOUND_PAYMENT", "message": "존재하지 않는 결제 정보 입니다."})

    gateway = TossPaymentGateway("test_sk_abc", "https://pg.example", transport=httpx.MockTransport(handler))

    with pytest.raises(PaymentGatewayError) as exc_info:
        asyncio.run(gateway.confirm("forged_key", "trendy-order-1", 20000))
    assert exc_info.value.code == "NOT_FOUND_PAYMENT"
    assert exc_info.value.retryable is False


def test_toss_gateway_without_secret_key_fails_closed():
    """시크릿 키가 없으면 결제를 승인된 것으로 취급하지 않고 실패해야 합니다."""
    gateway = TossPaymentGateway(None, "https://pg.example")

    with pytest.raises(PaymentGatewayError):
        asyncio.run(gateway.confirm("pg_key_123", "trendy-order-1", 20000))


# -----------------------------------------------------------------
# 재고 초과 판매 / 중복 재고 복구 / 결제 완료 주문 취소 (서비스 레벨)
# -----------------------------------------------------------------
def test_create_order_returns_409_when_atomic_stock_decrement_fails(monkeypatch):
    """사전 재고 확인은 통과했지만 트랜잭션 안의 조건부 차감에서 재고가 부족해진 경우 (동시 주문)"""
    _as(USER)

    async def fake_cart_find_by_id(cart_item_id):
        return {"id": cart_item_id, "userId": 1, "productId": 1, "quantity": 2}

    async def fake_product_find_by_id(product_id):
        return {"id": 1, "name": "상품", "price": 10000, "stock": 10, "isAvailable": True, "deletedAt": None}

    async def fake_create_order_with_items(**kwargs):
        raise orderRepository.InsufficientStockError(1)

    monkeypatch.setattr(cartRepository, "findById", fake_cart_find_by_id)
    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(orderRepository, "createOrderWithItems", fake_create_order_with_items)

    resp = client.post("/orders", json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": [1]})

    assert resp.status_code == status.HTTP_409_CONFLICT


def test_cancel_order_returns_409_when_status_changed_concurrently(monkeypatch):
    """조회 이후 다른 요청이 먼저 취소/배송 처리했다면 재고를 다시 복구하지 않고 409를 반환합니다."""
    _as(USER)

    async def fake_find_by_id(order_id):
        return _sample_order(status="PENDING", orderItems=[{"productId": 1, "quantity": 2}])

    async def fake_cancel_with_restock(order_id, order_items, from_statuses=None):
        raise orderRepository.OrderStatusConflictError(order_id)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(orderRepository, "cancelOrderWithRestock", fake_cancel_with_restock)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_409_CONFLICT


def test_user_cannot_cancel_paid_order_without_refund(monkeypatch):
    """환불 연동 전까지 사용자는 결제 완료 주문을 직접 취소할 수 없습니다."""
    _as(USER)

    async def fake_find_by_id(order_id):
        return _sample_order(status="PAID", orderItems=[{"productId": 1, "quantity": 2}])

    async def fake_cancel_with_restock(*args, **kwargs):
        raise AssertionError("사용자의 PAID 주문 취소는 차단되어야 합니다.")

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(orderRepository, "cancelOrderWithRestock", fake_cancel_with_restock)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_409_CONFLICT


def test_admin_can_cancel_paid_order_only_if_still_paid(monkeypatch):
    _as(ADMIN)

    async def fake_find_by_id(order_id):
        return _sample_order(status="PAID", orderItems=[{"productId": 1, "quantity": 2}])

    captured = {}

    async def fake_cancel_with_restock(order_id, order_items, from_statuses=None):
        captured["from_statuses"] = from_statuses
        return _sample_order(status="CANCELLED")

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(orderRepository, "cancelOrderWithRestock", fake_cancel_with_restock)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_200_OK
    assert captured["from_statuses"] == ["PAID"]


# -----------------------------------------------------------------
# 리포지토리 레벨: Prisma 호출 형태 검증 (가짜 트랜잭션)
# -----------------------------------------------------------------
class _FakeTx:
    """prisma.tx()가 돌려주는 트랜잭션 클라이언트를 흉내내며, 호출 기록과 update_many 결과를 제어합니다."""

    def __init__(self, update_many_results: dict[str, list[int]]):
        self.calls: list[tuple[str, str, dict]] = []
        self._results = {k: list(v) for k, v in update_many_results.items()}
        for model in ("product", "order", "payment", "cartitem"):
            setattr(self, model, self._model(model))

    def _model(self, model: str):
        tx = self

        async def update_many(**kwargs):
            tx.calls.append((model, "update_many", kwargs))
            return tx._results[model].pop(0)

        def recorder(method):
            async def _call(**kwargs):
                tx.calls.append((model, method, kwargs))
                return SimpleNamespace(model_dump=lambda: {"id": 1, "status": "X"})

            return _call

        return SimpleNamespace(
            update_many=update_many,
            update=recorder("update"),
            create=recorder("create"),
            find_unique=recorder("find_unique"),
            delete_many=recorder("delete_many"),
        )


def _install_fake_tx(monkeypatch, fake_tx):
    @asynccontextmanager
    async def fake_tx_ctx():
        yield fake_tx

    monkeypatch.setattr(orderRepository.prisma, "tx", fake_tx_ctx, raising=False)


def test_repository_stock_decrement_is_conditional_and_aborts_on_shortage(monkeypatch):
    fake_tx = _FakeTx({"product": [1, 0]})  # 첫 상품은 차감 성공, 두 번째 상품은 재고 부족
    _install_fake_tx(monkeypatch, fake_tx)

    items = [
        {"productId": 1, "price": 100, "quantity": 2, "totalPrice": 200},
        {"productId": 2, "price": 100, "quantity": 5, "totalPrice": 500},
    ]
    with pytest.raises(orderRepository.InsufficientStockError) as exc_info:
        asyncio.run(orderRepository.createOrderWithItems(1, "서울시 강남구", 700, items, [10, 11]))

    assert exc_info.value.product_id == 2
    first_where = fake_tx.calls[0][2]["where"]
    assert first_where["stock"] == {"gte": 2}
    assert first_where["isAvailable"] is True
    assert first_where["deletedAt"] is None
    # 재고 부족이 감지되면 주문 생성/장바구니 삭제까지 가지 않아야 합니다. (예외로 트랜잭션 롤백)
    assert not any(method in ("create", "delete_many") for _, method, _ in fake_tx.calls)


def test_repository_cancel_restocks_only_when_status_transition_succeeds(monkeypatch):
    fake_tx = _FakeTx({"order": [0]})  # 이미 다른 요청이 취소함
    _install_fake_tx(monkeypatch, fake_tx)

    with pytest.raises(orderRepository.OrderStatusConflictError):
        asyncio.run(orderRepository.cancelOrderWithRestock(1, [{"productId": 1, "quantity": 2}], ["PENDING"]))

    assert fake_tx.calls[0][2]["where"] == {"id": 1, "status": {"in": ["PENDING"]}}
    assert not any(model == "product" for model, _, _ in fake_tx.calls)


def test_repository_cancel_restocks_after_successful_transition(monkeypatch):
    fake_tx = _FakeTx({"order": [1]})
    _install_fake_tx(monkeypatch, fake_tx)

    asyncio.run(orderRepository.cancelOrderWithRestock(1, [{"productId": 7, "quantity": 3}], ["PAID"]))

    restocks = [kwargs for model, method, kwargs in fake_tx.calls if model == "product" and method == "update"]
    assert restocks == [{"where": {"id": 7}, "data": {"stock": {"increment": 3}}}]


def test_repository_mark_paid_is_compare_and_set_and_skips_payment_on_conflict(monkeypatch):
    fake_tx = _FakeTx({"order": [0]})
    _install_fake_tx(monkeypatch, fake_tx)

    with pytest.raises(orderRepository.OrderStatusConflictError):
        asyncio.run(orderRepository.markPaidWithPayment(1, "pg_key", "CARD", 20000))

    assert fake_tx.calls[0][2]["where"] == {"id": 1, "status": "PENDING"}
    assert not any(model == "payment" for model, _, _ in fake_tx.calls)
