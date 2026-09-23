from datetime import UTC, datetime

import pytest
from app.lib.passport.index import jwt_authenticate
from app.main import app
from app.repositories import AuthRepository as authRepository
from app.utils.cryptoUtil import hash_password
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)


def _sample_user(**overrides) -> dict:
    base = {
        "id": 1,
        "email": "user@test.com",
        "password": hash_password("password123"),
        "name": "홍길동",
        "role": "USER",
        "provider": "LOCAL",
        "providerId": None,
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


# -----------------------------------------------------------------
# 회원가입 (POST /auth/signup)
# -----------------------------------------------------------------
def test_signup_success(monkeypatch):
    async def fake_find_by_email(email):
        return None

    async def fake_create_user(user_dict):
        return _sample_user(email=user_dict["email"], name=user_dict["name"])

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)
    monkeypatch.setattr(authRepository, "createUser", fake_create_user)

    resp = client.post(
        "/auth/signup",
        json={
            "email": "new@test.com",
            "password": "password123",
            "name": "새유저",
        },
    )

    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["success"] is True
    assert "password" not in body["data"]


def test_signup_duplicate_email(monkeypatch):
    async def fake_find_by_email(email):
        return _sample_user(email=email)

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)

    resp = client.post(
        "/auth/signup",
        json={
            "email": "user@test.com",
            "password": "password123",
            "name": "중복유저",
        },
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


# -----------------------------------------------------------------
# 로그인 (POST /auth/login)
# -----------------------------------------------------------------
def test_login_success_returns_camel_case_tokens(monkeypatch):
    """
    회귀 테스트: AuthService.login이 access_token/refresh_token(스네이크케이스)을
    반환하던 버그가 있었습니다. TokenResponse 타입 및 /auth/refresh 응답과
    동일하게 accessToken/refreshToken(카멜케이스)으로 내려오는지 검증합니다.
    """

    async def fake_find_by_email(email):
        return _sample_user(email=email)

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)

    resp = client.post("/auth/login", json={"email": "user@test.com", "password": "password123"})

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()["data"]
    assert "accessToken" in data
    assert "refreshToken" in data
    assert "access_token" not in data
    assert "refresh_token" not in data


def test_login_wrong_password(monkeypatch):
    async def fake_find_by_email(email):
        return _sample_user(email=email)

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)

    resp = client.post("/auth/login", json={"email": "user@test.com", "password": "wrong-password"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_unknown_email(monkeypatch):
    async def fake_find_by_email(email):
        return None

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)

    resp = client.post("/auth/login", json={"email": "nobody@test.com", "password": "password123"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# -----------------------------------------------------------------
# 내 정보 조회 (GET /auth/me)
# -----------------------------------------------------------------
def test_me_requires_authentication():
    resp = client.get("/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_success(monkeypatch):
    app.dependency_overrides[jwt_authenticate] = lambda: _sample_user(id=1)

    async def fake_find_by_id(user_id):
        assert user_id == 1
        return _sample_user(id=1)

    monkeypatch.setattr(authRepository, "findUserById", fake_find_by_id)

    resp = client.get("/auth/me")

    # /auth/me는 response_model=UserResponse로 선언되어 있어, 다른 도메인들과
    # 달리 {success, message, data} 포장 없이 UserResponse 필드를 그대로 반환합니다.
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == "user@test.com"
