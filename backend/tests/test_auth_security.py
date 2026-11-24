"""
[인증 보안 회귀 테스트]

- 회원가입 시 role(권한) 주입으로 인한 권한 상승 차단
- 소셜 계정의 비밀번호 없는 로그인 차단
- 리프레시 토큰 저장/회전/재사용 탐지/로그아웃 폐기
- 토큰 만료 시간 환경변수 반영 및 쿠키 만료와의 일관성
- 내 정보 수정(PATCH /auth/updateMe) 인자 순서 버그
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from app.lib import env, token
from app.lib.passport.index import jwt_authenticate
from app.main import app
from app.repositories import AuthRepository as authRepository
from app.utils.cryptoUtil import hash_password
from fastapi import Response, status
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


class _FakeRefreshTokenStore:
    """AuthRepository의 리프레시 토큰 함수들을 대체하는 인메모리 저장소"""

    def __init__(self, monkeypatch):
        self.records: dict[str, dict] = {}
        self._next_id = 1
        monkeypatch.setattr(authRepository, "saveRefreshToken", self.save)
        monkeypatch.setattr(authRepository, "findRefreshTokenByHash", self.find)
        monkeypatch.setattr(authRepository, "rotateRefreshToken", self.rotate)
        monkeypatch.setattr(authRepository, "revokeAllRefreshTokens", self.revoke_all)

    async def save(self, user_id, token_hash, expires_at):
        self.records[token_hash] = {
            "id": self._next_id,
            "userId": int(user_id),
            "tokenHash": token_hash,
            "expiresAt": expires_at,
            "revokedAt": None,
        }
        self._next_id += 1

    async def find(self, token_hash):
        record = self.records.get(token_hash)
        return dict(record) if record else None

    async def rotate(self, old_id, user_id, new_hash, new_expires_at):
        old = next(r for r in self.records.values() if r["id"] == old_id)
        if old["revokedAt"] is not None:
            return False
        old["revokedAt"] = datetime.now(UTC)
        await self.save(user_id, new_hash, new_expires_at)
        return True

    async def revoke_all(self, user_id):
        count = 0
        for record in self.records.values():
            if record["userId"] == int(user_id) and record["revokedAt"] is None:
                record["revokedAt"] = datetime.now(UTC)
                count += 1
        return count

    def active_count(self, user_id=1):
        return sum(1 for r in self.records.values() if r["userId"] == user_id and r["revokedAt"] is None)


# -----------------------------------------------------------------
# 회원가입 권한 상승 차단 (CRITICAL 회귀 테스트)
# -----------------------------------------------------------------
@pytest.mark.parametrize("role", ["SUPER_ADMIN", "ADMIN", "USER"])
def test_signup_rejects_role_field(monkeypatch, role):
    """회원가입 바디에 role을 넣으면 조용히 무시하지 않고 422로 거부해야 합니다."""

    async def fake_create_user(user_dict):
        raise AssertionError("role이 포함된 가입 요청으로 유저가 생성되면 안 됩니다.")

    async def fake_find_by_email(email):
        return None

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)
    monkeypatch.setattr(authRepository, "createUser", fake_create_user)

    resp = client.post(
        "/auth/signup",
        json={"email": "evil@test.com", "password": "password123", "name": "공격자", "role": role},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_never_passes_role_to_repository(monkeypatch):
    captured = {}

    async def fake_find_by_email(email):
        return None

    async def fake_create_user(user_dict):
        captured.update(user_dict)
        return _sample_user(email=user_dict["email"], name=user_dict["name"])

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)
    monkeypatch.setattr(authRepository, "createUser", fake_create_user)

    resp = client.post("/auth/signup", json={"email": "new@test.com", "password": "password123", "name": "새유저"})

    assert resp.status_code == status.HTTP_201_CREATED
    assert "role" not in captured
    assert captured["provider"] == "LOCAL"
    assert captured["password"] != "password123"  # 해시되어 저장


def test_create_user_repository_always_assigns_user_role(monkeypatch):
    """리포지토리도 입력 dict의 role을 무시하고 항상 USER로 생성해야 합니다. (2중 방어)"""
    import asyncio
    from types import SimpleNamespace

    captured = {}

    async def fake_create(data):
        captured.update(data)
        return SimpleNamespace(model_dump=lambda: dict(data, id=1))

    monkeypatch.setattr(authRepository.prisma.user, "create", fake_create)

    asyncio.run(
        authRepository.createUser({"email": "a@test.com", "password": "x", "name": "에이", "role": "SUPER_ADMIN"})
    )

    assert captured["role"] == "USER"


def test_signup_rejects_social_provider_without_oauth(monkeypatch):
    """실제 OAuth 검증 없이 소셜 계정을 만들 수 없어야 합니다. (비밀번호 없는 계정 선점 방지)"""
    resp = client.post(
        "/auth/signup",
        json={"email": "victim@test.com", "name": "피해자", "provider": "KAKAO", "providerId": "123"},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_local_login_rejects_social_account_without_password(monkeypatch):
    """기존에는 provider가 LOCAL이 아니면 비밀번호 검증 없이 로그인되었습니다."""

    async def fake_find_by_email(email):
        return _sample_user(email=email, provider="KAKAO", providerId="kakao-1", password=None)

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)

    resp = client.post("/auth/login", json={"email": "victim@test.com", "password": "anything"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# -----------------------------------------------------------------
# 리프레시 토큰 저장/회전/폐기
# -----------------------------------------------------------------
def _login(monkeypatch) -> dict:
    async def fake_find_by_email(email):
        return _sample_user(email=email)

    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)
    resp = client.post("/auth/login", json={"email": "user@test.com", "password": "password123"})
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["data"]


def test_login_persists_hashed_refresh_token(monkeypatch):
    store = _FakeRefreshTokenStore(monkeypatch)

    tokens = _login(monkeypatch)

    assert token.hashToken(tokens["refreshToken"]) in store.records
    # 원문은 저장하지 않습니다.
    assert tokens["refreshToken"] not in store.records
    assert "refreshTokenExpiresAt" not in tokens


def test_refresh_rotates_token_and_old_token_cannot_be_reused(monkeypatch):
    store = _FakeRefreshTokenStore(monkeypatch)
    tokens = _login(monkeypatch)

    first = client.post("/auth/refresh", json={"refreshToken": tokens["refreshToken"]})
    assert first.status_code == status.HTTP_200_OK
    rotated = first.json()["data"]
    assert rotated["refreshToken"] != tokens["refreshToken"]

    # 이미 사용(회전)된 토큰 재사용 → 401, 그리고 탈취 의심으로 해당 유저의 모든 리프레시 토큰 폐기
    reuse = client.post("/auth/refresh", json={"refreshToken": tokens["refreshToken"]})
    assert reuse.status_code == status.HTTP_401_UNAUTHORIZED
    assert store.active_count() == 0

    # 새로 받은 토큰도 함께 폐기되었으므로 사용할 수 없습니다.
    after = client.post("/auth/refresh", json={"refreshToken": rotated["refreshToken"]})
    assert after.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_rejects_valid_jwt_that_was_never_stored(monkeypatch):
    """서명은 유효하더라도 서버가 발급/저장한 적 없는 토큰은 거부합니다."""
    _FakeRefreshTokenStore(monkeypatch)
    forged = token.generateTokens(1)["refreshToken"]

    resp = client.post("/auth/refresh", json={"refreshToken": forged})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_revokes_refresh_tokens(monkeypatch):
    store = _FakeRefreshTokenStore(monkeypatch)
    tokens = _login(monkeypatch)
    assert store.active_count() == 1

    app.dependency_overrides[jwt_authenticate] = lambda: _sample_user(id=1)
    resp = client.post("/auth/logout")
    assert resp.status_code == status.HTTP_200_OK
    assert store.active_count() == 0

    refresh_resp = client.post("/auth/refresh", json={"refreshToken": tokens["refreshToken"]})
    assert refresh_resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_cannot_be_used_as_access_token(monkeypatch):
    """액세스/리프레시 시크릿을 같게 설정한 경우에도 리프레시 토큰으로 API에 접근할 수 없어야 합니다."""
    from app.lib.passport import jwtStrategy

    monkeypatch.setattr(jwtStrategy, "JWT_ACCESS_TOKEN_SECRET", env.JWT_REFRESH_TOKEN_SECRET)

    async def fake_find_by_id(user_id):
        return _sample_user(id=1)

    monkeypatch.setattr(authRepository, "findUserById", fake_find_by_id)
    refresh_token = token.generateTokens(1)["refreshToken"]

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# -----------------------------------------------------------------
# 토큰 만료 시간 설정
# -----------------------------------------------------------------
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, timedelta(days=7)),
        ("", timedelta(days=7)),
        ("3600", timedelta(hours=1)),
        ("30s", timedelta(seconds=30)),
        ("15m", timedelta(minutes=15)),
        ("2h", timedelta(hours=2)),
        ("14d", timedelta(days=14)),
    ],
)
def test_parse_duration(raw, expected):
    assert env.parse_duration(raw, timedelta(days=7)) == expected


@pytest.mark.parametrize("raw", ["abc", "-1h", "0", "1w"])
def test_parse_duration_rejects_invalid_values(raw):
    with pytest.raises(ValueError):
        env.parse_duration(raw, timedelta(days=7))


def test_token_exp_follows_configured_ttl(monkeypatch):
    monkeypatch.setattr(token, "ACCESS_TOKEN_TTL", timedelta(minutes=15))
    monkeypatch.setattr(token, "REFRESH_TOKEN_TTL", timedelta(days=14))

    tokens = token.generateTokens(1)
    access = jwt.decode(tokens["accessToken"], env.JWT_ACCESS_TOKEN_SECRET, algorithms=[env.JWT_ALGORITHM])
    refresh = jwt.decode(tokens["refreshToken"], env.JWT_REFRESH_TOKEN_SECRET, algorithms=[env.JWT_ALGORITHM])

    access_ttl = access["exp"] - datetime.now(UTC).timestamp()
    refresh_ttl = refresh["exp"] - datetime.now(UTC).timestamp()
    assert 14 * 60 < access_ttl <= 15 * 60
    assert 14 * 86400 - 60 < refresh_ttl <= 14 * 86400


def test_refresh_cookie_max_age_matches_refresh_token_ttl():
    """기존에는 리프레시 JWT 만료(1일)와 쿠키 max_age(7일)가 서로 달랐습니다."""
    res = Response()
    token.setTokenCookies(res, "a", "r")
    cookies = res.headers.getlist("set-cookie")

    assert any(f"Max-Age={int(env.ACCESS_TOKEN_TTL.total_seconds())}" in c for c in cookies if c.startswith("access"))
    assert any(f"Max-Age={int(env.REFRESH_TOKEN_TTL.total_seconds())}" in c for c in cookies if c.startswith("refresh"))


# -----------------------------------------------------------------
# 내 정보 수정 (기존에 라우터가 컨트롤러 인자 순서를 뒤바꿔 호출하던 버그)
# -----------------------------------------------------------------
def test_update_me_success(monkeypatch):
    app.dependency_overrides[jwt_authenticate] = lambda: _sample_user(id=1)
    captured = {}

    async def fake_find_by_id(user_id):
        return _sample_user(id=1)

    async def fake_find_by_email(email):
        return None

    async def fake_update_user(user_id, update_data):
        captured["user_id"] = user_id
        captured["data"] = update_data
        return _sample_user(id=1, email=update_data["email"], name=update_data["name"])

    monkeypatch.setattr(authRepository, "findUserById", fake_find_by_id)
    monkeypatch.setattr(authRepository, "findUserByEmail", fake_find_by_email)
    monkeypatch.setattr(authRepository, "updateUser", fake_update_user)

    resp = client.patch("/auth/updateMe", json={"email": "changed@test.com", "name": "새이름"})

    assert resp.status_code == status.HTTP_200_OK
    assert captured == {"user_id": 1, "data": {"email": "changed@test.com", "name": "새이름"}}
    assert "password" not in resp.json()["data"]


def test_update_me_validates_body():
    app.dependency_overrides[jwt_authenticate] = lambda: _sample_user(id=1)

    resp = client.patch("/auth/updateMe", json={"email": "not-an-email", "name": "새이름"})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
