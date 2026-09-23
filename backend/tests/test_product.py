from datetime import UTC, datetime

import pytest
from app.lib.passport.roleGuard import require_admin
from app.main import app
from app.repositories import ProductRepository as productRepository
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)


def _sample_product(**overrides) -> dict:
    base = {
        "id": 1,
        "name": "테스트 상품",
        "description": "설명입니다.",
        "price": 10000,
        "stock": 5,
        "isAvailable": True,
        "images": [],
        "deletedAt": None,
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }
    base.update(overrides)
    return base


ADMIN_USER = {"id": 1, "email": "admin@test.com", "role": "ADMIN"}
NORMAL_USER = {"id": 2, "email": "user@test.com", "role": "USER"}


def _forbidden_admin_override():
    # require_admin이 일반 유저를 만났을 때와 동일하게 403을 발생시키는 테스트용 대체 함수
    raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")


@pytest.fixture(autouse=True)
def _clear_overrides():
    # 각 테스트가 끝나면 의존성 오버라이드를 초기화해서 테스트 간 간섭을 막습니다.
    yield
    app.dependency_overrides.clear()


# -----------------------------------------------------------------
# 목록 조회 (GET /products)
# -----------------------------------------------------------------
def test_list_products_success(monkeypatch):
    products = [_sample_product(id=1), _sample_product(id=2, name="상품2")]

    async def fake_find_many(**kwargs):
        return products, len(products)

    monkeypatch.setattr(productRepository, "findMany", fake_find_many)

    resp = client.get("/products")

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]["items"]) == 2
    assert body["data"]["meta"]["totalCount"] == 2
    assert body["data"]["meta"]["currentPage"] == 1


def test_list_products_pagination_meta(monkeypatch):
    async def fake_find_many(**kwargs):
        # 총 25개 중 페이지당 20개 -> 2페이지가 되어야 함
        return [_sample_product(id=i) for i in range(20)], 25

    monkeypatch.setattr(productRepository, "findMany", fake_find_many)

    resp = client.get("/products?page=1&limit=20")

    meta = resp.json()["data"]["meta"]
    assert meta["totalPages"] == 2
    assert meta["hasNextPage"] is True
    assert meta["hasPrevPage"] is False


def test_list_products_invalid_query_returns_422(monkeypatch):
    # limit은 100 이하로 제한되어 있음 (ProductSearchQuery)
    resp = client.get("/products?limit=9999")
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 상세 조회 (GET /products/{id})
# -----------------------------------------------------------------
def test_get_product_success(monkeypatch):
    async def fake_find_by_id(product_id):
        assert product_id == 1
        return _sample_product(id=1)

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)

    resp = client.get("/products/1")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["id"] == 1


def test_get_product_not_found(monkeypatch):
    async def fake_find_by_id(product_id):
        return None

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)

    resp = client.get("/products/999")

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["success"] is False
    assert resp.json()["error"]["code"] == "HTTP_404"


def test_get_product_soft_deleted_treated_as_not_found(monkeypatch):
    async def fake_find_by_id(product_id):
        return _sample_product(id=1, deletedAt=datetime.now(UTC))

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)

    resp = client.get("/products/1")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


# -----------------------------------------------------------------
# 등록 (POST /products) - 관리자 전용
# -----------------------------------------------------------------
def test_create_product_requires_authentication():
    resp = client.post(
        "/products",
        json={"name": "새 상품", "price": 1000, "stock": 10},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_product_forbidden_for_normal_user():
    app.dependency_overrides[require_admin] = _forbidden_admin_override

    resp = client.post(
        "/products",
        json={"name": "새 상품", "price": 1000, "stock": 10},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_create_product_success_as_admin(monkeypatch):
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER

    async def fake_create(data):
        assert data["name"] == "새 상품"
        assert data["price"] == 1000
        assert data["stock"] == 10
        return _sample_product(id=10, name="새 상품", price=1000, stock=10)

    monkeypatch.setattr(productRepository, "create", fake_create)

    resp = client.post(
        "/products",
        json={"name": "새 상품", "price": 1000, "stock": 10},
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["data"]["name"] == "새 상품"


def test_create_product_validation_error_negative_price():
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER

    resp = client.post(
        "/products",
        json={"name": "새 상품", "price": -1000, "stock": 10},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 수정 (PATCH /products/{id}) - 관리자 전용
# -----------------------------------------------------------------
def test_update_product_success_as_admin(monkeypatch):
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER

    async def fake_find_by_id(product_id):
        return _sample_product(id=1)

    async def fake_update(product_id, data):
        assert product_id == 1
        assert data["price"] == 20000
        return _sample_product(id=1, price=20000)

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(productRepository, "update", fake_update)

    resp = client.patch("/products/1", json={"price": 20000})

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["price"] == 20000


def test_update_product_not_found_as_admin(monkeypatch):
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER

    async def fake_find_by_id(product_id):
        return None

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)

    resp = client.patch("/products/999", json={"price": 20000})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


# -----------------------------------------------------------------
# 삭제 (DELETE /products/{id}) - 관리자 전용, 소프트 딜리트
# -----------------------------------------------------------------
def test_delete_product_success_as_admin(monkeypatch):
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER

    async def fake_find_by_id(product_id):
        return _sample_product(id=1)

    soft_delete_called_with = {}

    async def fake_soft_delete(product_id):
        soft_delete_called_with["product_id"] = product_id
        return _sample_product(id=1, isAvailable=False, deletedAt=datetime.now(UTC))

    monkeypatch.setattr(productRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(productRepository, "softDelete", fake_soft_delete)

    resp = client.delete("/products/1")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["success"] is True
    assert soft_delete_called_with["product_id"] == 1


def test_delete_product_forbidden_for_normal_user():
    app.dependency_overrides[require_admin] = _forbidden_admin_override

    resp = client.delete("/products/1")

    assert resp.status_code == status.HTTP_403_FORBIDDEN
