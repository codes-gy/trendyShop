from datetime import UTC, datetime

import pytest
from app.lib.passport.index import jwt_authenticate
from app.main import app
from app.repositories import CartRepository as cartRepository
from app.repositories import ProductRepository as productRepository
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

USER = {"id": 1, "email": "user@test.com", "role": "USER"}
OTHER_USER = {"id": 2, "email": "other@test.com", "role": "USER"}


def _sample_product(**overrides) -> dict:
    base = {
        "id": 1,
        "name": "테스트 상품",
        "description": None,
        "price": 10000,
        "stock": 10,
        "isAvailable": True,
        "images": [],
        "deletedAt": None,
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }
    base.update(overrides)
    return base


def _sample_cart_item(**overrides) -> dict:
    base = {
        "id": 1,
        "userId": 1,
        "productId": 1,
        "quantity": 2,
        "product": _sample_product(),
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
# 목록 조회 (GET /cart)
# -----------------------------------------------------------------
def test_list_cart_requires_authentication():
    resp = client.get("/cart")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_cart_success(monkeypatch):
    _as_user()

    async def fake_find_many_by_user(user_id):
        assert user_id == 1
        return [_sample_cart_item(id=1), _sample_cart_item(id=2, productId=2)]

    monkeypatch.setattr(cartRepository, "findManyByUser", fake_find_many_by_user)

    resp = client.get("/cart")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["data"]) == 2


# -----------------------------------------------------------------
# 담기 (POST /cart)
# -----------------------------------------------------------------
def test_add_item_new_success(monkeypatch):
    _as_user()

    async def fake_find_by_id(product_id):
        return _sample_product(id=1, stock=10)

    async def fake_find_existing(user_id, product_id):
        return None

    async def fake_create(user_id, product_id, quantity):
        assert user_id == 1
        assert product_id == 1
        assert quantity == 3
        return _sample_cart_item(id=1, quantity=3)

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(cartRepository, "findByUserAndProduct", fake_find_existing)
    monkeypatch.setattr(cartRepository, "create", fake_create)

    resp = client.post("/cart", json={"productId": 1, "quantity": 3})

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["data"]["quantity"] == 3


def test_add_item_merges_with_existing(monkeypatch):
    _as_user()

    async def fake_find_by_id(product_id):
        return _sample_product(id=1, stock=10)

    async def fake_find_existing(user_id, product_id):
        return _sample_cart_item(id=5, quantity=2)

    async def fake_update_quantity(cart_item_id, quantity):
        assert cart_item_id == 5
        assert quantity == 5  # 기존 2개 + 새로 담은 3개
        return _sample_cart_item(id=5, quantity=5)

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(cartRepository, "findByUserAndProduct", fake_find_existing)
    monkeypatch.setattr(cartRepository, "updateQuantity", fake_update_quantity)

    resp = client.post("/cart", json={"productId": 1, "quantity": 3})

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["data"]["quantity"] == 5


def test_add_item_exceeds_stock(monkeypatch):
    _as_user()

    async def fake_find_by_id(product_id):
        return _sample_product(id=1, stock=2)

    async def fake_find_existing(user_id, product_id):
        return None

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(cartRepository, "findByUserAndProduct", fake_find_existing)

    resp = client.post("/cart", json={"productId": 1, "quantity": 3})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_add_item_unavailable_product(monkeypatch):
    _as_user()

    async def fake_find_by_id(product_id):
        return _sample_product(id=1, isAvailable=False)

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)

    resp = client.post("/cart", json={"productId": 1, "quantity": 1})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_add_item_product_not_found(monkeypatch):
    _as_user()

    async def fake_find_by_id(product_id):
        return None

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)

    resp = client.post("/cart", json={"productId": 999, "quantity": 1})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_add_item_invalid_quantity_returns_422():
    _as_user()

    resp = client.post("/cart", json={"productId": 1, "quantity": 0})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 수량 변경 (PATCH /cart/{id})
# -----------------------------------------------------------------
def test_update_item_success(monkeypatch):
    _as_user()

    async def fake_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, userId=1, productId=1, quantity=2)

    async def fake_find_product(product_id):
        return _sample_product(id=1, stock=10)

    async def fake_update_quantity(cart_item_id, quantity):
        assert cart_item_id == 1
        assert quantity == 5
        return _sample_cart_item(id=1, quantity=5)

    monkeypatch.setattr(cartRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(productRepository, "findById", fake_find_product)
    monkeypatch.setattr(cartRepository, "updateQuantity", fake_update_quantity)

    resp = client.patch("/cart/1", json={"quantity": 5})

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["quantity"] == 5


def test_update_item_not_found(monkeypatch):
    _as_user()

    async def fake_find_by_id(cart_item_id):
        return None

    monkeypatch.setattr(cartRepository, "findById", fake_find_by_id)

    resp = client.patch("/cart/999", json={"quantity": 5})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_item_forbidden_for_other_users_item(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, userId=2)  # 다른 유저 소유

    monkeypatch.setattr(cartRepository, "findById", fake_find_by_id)

    resp = client.patch("/cart/1", json={"quantity": 5})

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_update_item_exceeds_stock(monkeypatch):
    _as_user()

    async def fake_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, userId=1, productId=1, quantity=2)

    async def fake_find_product(product_id):
        return _sample_product(id=1, stock=3)

    monkeypatch.setattr(cartRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(productRepository, "findById", fake_find_product)

    resp = client.patch("/cart/1", json={"quantity": 10})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


# -----------------------------------------------------------------
# 삭제 (DELETE /cart/{id})
# -----------------------------------------------------------------
def test_remove_item_success(monkeypatch):
    _as_user()

    async def fake_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, userId=1)

    deleted_with = {}

    async def fake_delete(cart_item_id):
        deleted_with["id"] = cart_item_id

    monkeypatch.setattr(cartRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(cartRepository, "delete", fake_delete)

    resp = client.delete("/cart/1")

    assert resp.status_code == status.HTTP_200_OK
    assert deleted_with["id"] == 1


def test_remove_item_forbidden_for_other_users_item(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(cart_item_id):
        return _sample_cart_item(id=1, userId=2)

    monkeypatch.setattr(cartRepository, "findById", fake_find_by_id)

    resp = client.delete("/cart/1")

    assert resp.status_code == status.HTTP_403_FORBIDDEN
