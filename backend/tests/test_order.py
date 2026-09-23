from datetime import UTC, datetime

import pytest
from app.lib.passport.index import jwt_authenticate
from app.main import app
from app.repositories import CartRepository as cartRepository
from app.repositories import OrderRepository as orderRepository
from app.repositories import ProductRepository as productRepository
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

USER = {"id": 1, "email": "user@test.com", "role": "USER"}


def _sample_product(**overrides) -> dict:
    base = {
        "id": 1,
        "name": "테스트 상품",
        "price": 10000,
        "stock": 10,
        "isAvailable": True,
        "deletedAt": None,
    }
    base.update(overrides)
    return base


def _sample_cart_item(**overrides) -> dict:
    base = {"id": 1, "userId": 1, "productId": 1, "quantity": 2}
    base.update(overrides)
    return base


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


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _as_user(user=USER):
    app.dependency_overrides[jwt_authenticate] = lambda: user


# -----------------------------------------------------------------
# 목록/상세 조회
# -----------------------------------------------------------------
def test_list_orders_requires_authentication():
    resp = client.get("/orders")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_orders_success(monkeypatch):
    _as_user()

    async def fake_find_many_by_user(user_id):
        assert user_id == 1
        return [_sample_order(id=1), _sample_order(id=2)]

    monkeypatch.setattr(orderRepository, "findManyByUser", fake_find_many_by_user)

    resp = client.get("/orders")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["data"]) == 2


def test_get_order_success(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=1)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.get("/orders/1")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["id"] == 1


def test_get_order_not_found(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return None

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.get("/orders/999")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_order_forbidden_for_other_users_order(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=2)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.get("/orders/1")

    assert resp.status_code == status.HTTP_403_FORBIDDEN


# -----------------------------------------------------------------
# 주문 생성 (체크아웃)
# -----------------------------------------------------------------
def test_create_order_success(monkeypatch):
    _as_user()

    async def fake_cart_find_by_id(cart_item_id):
        return _sample_cart_item(id=cart_item_id, quantity=2)

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=product_id, price=10000, stock=10)

    captured = {}

    async def fake_create_order_with_items(**kwargs):
        captured.update(kwargs)
        return _sample_order(id=1, totalPrice=kwargs["total_price"])

    monkeypatch.setattr(cartRepository, "findById", fake_cart_find_by_id)
    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(orderRepository, "createOrderWithItems", fake_create_order_with_items)

    resp = client.post(
        "/orders",
        json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": [1]},
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert captured["total_price"] == 20000  # 10000 * 2
    assert captured["cart_item_ids"] == [1]
    assert resp.json()["data"]["totalPrice"] == 20000


def test_create_order_cart_item_not_found(monkeypatch):
    _as_user()

    async def fake_cart_find_by_id(cart_item_id):
        return None

    monkeypatch.setattr(cartRepository, "findById", fake_cart_find_by_id)

    resp = client.post(
        "/orders",
        json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": [999]},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_create_order_cart_item_owned_by_other_user(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_cart_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, userId=2)

    monkeypatch.setattr(cartRepository, "findById", fake_cart_find_by_id)

    resp = client.post(
        "/orders",
        json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": [1]},
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_create_order_product_unavailable(monkeypatch):
    _as_user()

    async def fake_cart_find_by_id(cart_item_id):
        return _sample_cart_item(id=1)

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=1, isAvailable=False)

    monkeypatch.setattr(cartRepository, "findById", fake_cart_find_by_id)
    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)

    resp = client.post(
        "/orders",
        json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": [1]},
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_order_insufficient_stock(monkeypatch):
    _as_user()

    async def fake_cart_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, quantity=5)

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=1, stock=2)

    monkeypatch.setattr(cartRepository, "findById", fake_cart_find_by_id)
    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)

    resp = client.post(
        "/orders",
        json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": [1]},
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_order_empty_cart_item_ids_returns_422():
    _as_user()

    resp = client.post(
        "/orders",
        json={"address": "서울시 강남구 테헤란로 1", "cartItemIds": []},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_order_short_address_returns_422():
    _as_user()

    resp = client.post(
        "/orders",
        json={"address": "짧음", "cartItemIds": [1]},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 결제 승인
# -----------------------------------------------------------------
def test_approve_payment_success(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=1, status="PENDING", totalPrice=20000)

    async def fake_create_payment(order_id, payment_key, method, amount):
        assert order_id == 1
        assert amount == 20000
        return {"id": 1}

    async def fake_update_status(order_id, order_status):
        assert order_status == "PAID"
        return _sample_order(id=1, status="PAID", totalPrice=20000)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(orderRepository, "createPayment", fake_create_payment)
    monkeypatch.setattr(orderRepository, "updateStatus", fake_update_status)

    resp = client.post(
        "/orders/payment",
        json={
            "orderId": 1,
            "paymentKey": "pg_key_123",
            "amount": 20000,
            "method": "CARD",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["status"] == "PAID"


def test_approve_payment_amount_mismatch(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=1, status="PENDING", totalPrice=20000)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.post(
        "/orders/payment",
        json={
            "orderId": 1,
            "paymentKey": "pg_key_123",
            "amount": 999,
            "method": "CARD",
        },
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_approve_payment_already_paid(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=1, status="PAID", totalPrice=20000)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.post(
        "/orders/payment",
        json={
            "orderId": 1,
            "paymentKey": "pg_key_123",
            "amount": 20000,
            "method": "CARD",
        },
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_approve_payment_forbidden_for_other_users_order(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=2, status="PENDING", totalPrice=20000)

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.post(
        "/orders/payment",
        json={
            "orderId": 1,
            "paymentKey": "pg_key_123",
            "amount": 20000,
            "method": "CARD",
        },
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_approve_payment_negative_amount_returns_422():
    _as_user()

    resp = client.post(
        "/orders/payment",
        json={
            "orderId": 1,
            "paymentKey": "pg_key_123",
            "amount": -1,
            "method": "CARD",
        },
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 주문 취소 (PATCH /orders/{id}/cancel)
# -----------------------------------------------------------------
def test_cancel_order_requires_authentication():
    resp = client.patch("/orders/1/cancel")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_cancel_order_success_restocks_products(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(
            id=1,
            userId=1,
            status="PAID",
            orderItems=[
                {"productId": 1, "quantity": 2},
                {"productId": 2, "quantity": 3},
            ],
        )

    captured = {}

    async def fake_cancel_with_restock(order_id, order_items):
        captured["order_id"] = order_id
        captured["order_items"] = order_items
        return _sample_order(id=1, status="CANCELLED")

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(orderRepository, "cancelOrderWithRestock", fake_cancel_with_restock)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["status"] == "CANCELLED"
    assert captured["order_id"] == 1
    assert captured["order_items"] == [
        {"productId": 1, "quantity": 2},
        {"productId": 2, "quantity": 3},
    ]


def test_cancel_order_not_found(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return None

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.patch("/orders/999/cancel")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_cancel_order_forbidden_for_other_users_order(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=2, status="PAID")

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_cancel_order_already_shipped_rejected(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=1, status="SHIPPED")

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_cancel_order_already_cancelled_rejected(monkeypatch):
    _as_user()

    async def fake_find_by_id(order_id):
        return _sample_order(id=1, userId=1, status="CANCELLED")

    monkeypatch.setattr(orderRepository, "findById", fake_find_by_id)

    resp = client.patch("/orders/1/cancel")

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
