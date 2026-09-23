from datetime import UTC, datetime

import pytest
from app.lib.passport.index import jwt_authenticate
from app.main import app
from app.repositories import OrderRepository as orderRepository
from app.repositories import ProductRepository as productRepository
from app.repositories import ReviewRepository as reviewRepository
from fastapi import status
from fastapi.testclient import TestClient
from prisma.errors import UniqueViolationError

client = TestClient(app, raise_server_exceptions=False)

USER = {"id": 1, "email": "user@test.com", "role": "USER"}
ADMIN_USER = {"id": 9, "email": "admin@test.com", "role": "ADMIN"}


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


def _sample_review(**overrides) -> dict:
    base = {
        "id": 1,
        "userId": 1,
        "productId": 1,
        "rating": 5,
        "comment": "정말 좋은 상품이었어요!",
        "user": None,
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
# 목록 조회 (GET /reviews)
# -----------------------------------------------------------------
def test_list_reviews_success(monkeypatch):
    async def fake_product_find_by_id(product_id):
        return _sample_product(id=product_id)

    async def fake_find_many_by_product(product_id, page, limit):
        return [_sample_review(id=1), _sample_review(id=2)], 2

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(reviewRepository, "findManyByProduct", fake_find_many_by_product)

    resp = client.get("/reviews?productId=1")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["data"]["items"]) == 2


def test_list_reviews_product_not_found(monkeypatch):
    async def fake_product_find_by_id(product_id):
        return None

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)

    resp = client.get("/reviews?productId=999")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_list_reviews_missing_product_id_returns_422():
    resp = client.get("/reviews")
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 작성 (POST /reviews)
# -----------------------------------------------------------------
def test_create_review_requires_authentication():
    resp = client.post("/reviews", json={"productId": 1, "rating": 5, "comment": "좋아요 좋아요"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_review_success(monkeypatch):
    _as_user()

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=1)

    async def fake_has_purchased(user_id, product_id):
        assert user_id == 1
        assert product_id == 1
        return True

    async def fake_find_existing(user_id, product_id):
        return None

    async def fake_create(user_id, product_id, rating, comment):
        return _sample_review(rating=rating, comment=comment)

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(orderRepository, "hasPurchasedProduct", fake_has_purchased)
    monkeypatch.setattr(reviewRepository, "findByUserAndProduct", fake_find_existing)
    monkeypatch.setattr(reviewRepository, "create", fake_create)

    resp = client.post("/reviews", json={"productId": 1, "rating": 5, "comment": "정말 만족스러워요"})

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["data"]["rating"] == 5


def test_create_review_forbidden_without_purchase(monkeypatch):
    _as_user()

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=1)

    async def fake_has_purchased(user_id, product_id):
        return False

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(orderRepository, "hasPurchasedProduct", fake_has_purchased)

    resp = client.post("/reviews", json={"productId": 1, "rating": 5, "comment": "정말 만족스러워요"})

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_create_review_duplicate_rejected(monkeypatch):
    _as_user()

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=1)

    async def fake_has_purchased(user_id, product_id):
        return True

    async def fake_find_existing(user_id, product_id):
        return _sample_review(id=1)

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(orderRepository, "hasPurchasedProduct", fake_has_purchased)
    monkeypatch.setattr(reviewRepository, "findByUserAndProduct", fake_find_existing)

    resp = client.post("/reviews", json={"productId": 1, "rating": 5, "comment": "정말 만족스러워요"})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_review_race_condition_db_constraint_rejected(monkeypatch):
    # 애플리케이션 레벨 중복 체크는 통과했지만(동시 요청), DB 유니크 제약이 막아주는 경우
    _as_user()

    async def fake_product_find_by_id(product_id):
        return _sample_product(id=1)

    async def fake_has_purchased(user_id, product_id):
        return True

    async def fake_find_existing(user_id, product_id):
        return None

    async def fake_create(user_id, product_id, rating, comment):
        raise UniqueViolationError({}, message="duplicate key value violates unique constraint")

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)
    monkeypatch.setattr(orderRepository, "hasPurchasedProduct", fake_has_purchased)
    monkeypatch.setattr(reviewRepository, "findByUserAndProduct", fake_find_existing)
    monkeypatch.setattr(reviewRepository, "create", fake_create)

    resp = client.post("/reviews", json={"productId": 1, "rating": 5, "comment": "정말 만족스러워요"})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_review_product_not_found(monkeypatch):
    _as_user()

    async def fake_product_find_by_id(product_id):
        return None

    monkeypatch.setattr(productRepository, "findById", fake_product_find_by_id)

    resp = client.post("/reviews", json={"productId": 999, "rating": 5, "comment": "정말 만족스러워요"})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_create_review_comment_too_short_returns_422():
    _as_user()

    resp = client.post("/reviews", json={"productId": 1, "rating": 5, "comment": "짧음"})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_review_rating_out_of_range_returns_422():
    _as_user()

    resp = client.post("/reviews", json={"productId": 1, "rating": 6, "comment": "정말 만족스러워요"})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -----------------------------------------------------------------
# 수정 (PATCH /reviews/{id})
# -----------------------------------------------------------------
def test_update_review_success(monkeypatch):
    _as_user()

    async def fake_find_by_id(review_id):
        return _sample_review(id=1, userId=1)

    async def fake_update(review_id, data):
        assert data["rating"] == 3
        return _sample_review(id=1, rating=3)

    monkeypatch.setattr(reviewRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(reviewRepository, "update", fake_update)

    resp = client.patch("/reviews/1", json={"rating": 3})

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["rating"] == 3


def test_update_review_forbidden_for_other_users_review(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(review_id):
        return _sample_review(id=1, userId=2)

    monkeypatch.setattr(reviewRepository, "findById", fake_find_by_id)

    resp = client.patch("/reviews/1", json={"rating": 3})

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_update_review_not_found(monkeypatch):
    _as_user()

    async def fake_find_by_id(review_id):
        return None

    monkeypatch.setattr(reviewRepository, "findById", fake_find_by_id)

    resp = client.patch("/reviews/999", json={"rating": 3})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


# -----------------------------------------------------------------
# 삭제 (DELETE /reviews/{id})
# -----------------------------------------------------------------
def test_delete_review_success_as_owner(monkeypatch):
    _as_user()

    async def fake_find_by_id(review_id):
        return _sample_review(id=1, userId=1)

    deleted_with = {}

    async def fake_delete(review_id):
        deleted_with["id"] = review_id

    monkeypatch.setattr(reviewRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(reviewRepository, "delete", fake_delete)

    resp = client.delete("/reviews/1")

    assert resp.status_code == status.HTTP_200_OK
    assert deleted_with["id"] == 1


def test_delete_review_forbidden_for_other_users_review(monkeypatch):
    _as_user(USER)  # id=1

    async def fake_find_by_id(review_id):
        return _sample_review(id=1, userId=2)

    monkeypatch.setattr(reviewRepository, "findById", fake_find_by_id)

    resp = client.delete("/reviews/1")

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_delete_review_success_as_admin_for_other_users_review(monkeypatch):
    _as_user(ADMIN_USER)  # id=9, role=ADMIN

    async def fake_find_by_id(review_id):
        return _sample_review(id=1, userId=1)  # 관리자 본인 리뷰 아님

    deleted_with = {}

    async def fake_delete(review_id):
        deleted_with["id"] = review_id

    monkeypatch.setattr(reviewRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(reviewRepository, "delete", fake_delete)

    resp = client.delete("/reviews/1")

    assert resp.status_code == status.HTTP_200_OK
    assert deleted_with["id"] == 1
