from datetime import UTC, datetime

import pytest
from app.lib.passport.roleGuard import require_admin
from app.main import app
from app.repositories import AdminRepository as adminRepository
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

ADMIN = {"id": 1, "email": "admin@test.com", "role": "ADMIN"}
SUPER_ADMIN = {"id": 2, "email": "super@test.com", "role": "SUPER_ADMIN"}


def _sample_user(**overrides) -> dict:
    base = {
        "id": 10,
        "email": "member@test.com",
        "name": "회원",
        "role": "USER",
        "provider": "LOCAL",
        "providerId": None,
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }
    base.update(overrides)
    return base


def _forbidden_admin_override():
    raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _as(actor):
    app.dependency_overrides[require_admin] = lambda: actor


# -----------------------------------------------------------------
# 회원 목록 (GET /admin/users)
# -----------------------------------------------------------------
def test_list_users_requires_authentication():
    resp = client.get("/admin/users")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_users_forbidden_for_normal_user():
    app.dependency_overrides[require_admin] = _forbidden_admin_override
    resp = client.get("/admin/users")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_list_users_success(monkeypatch):
    _as(ADMIN)

    async def fake_find_many_users(keyword, role, page, limit):
        return [_sample_user(id=1), _sample_user(id=2)], 2

    monkeypatch.setattr(adminRepository, "findManyUsers", fake_find_many_users)

    resp = client.get("/admin/users")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["data"]["items"]) == 2


# -----------------------------------------------------------------
# 회원 상세 (GET /admin/users/{id})
# -----------------------------------------------------------------
def test_get_user_success(monkeypatch):
    _as(ADMIN)

    async def fake_find_user_by_id(user_id):
        return _sample_user(id=10)

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)

    resp = client.get("/admin/users/10")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["id"] == 10


def test_get_user_not_found(monkeypatch):
    _as(ADMIN)

    async def fake_find_user_by_id(user_id):
        return None

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)

    resp = client.get("/admin/users/999")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


# -----------------------------------------------------------------
# 권한 변경 (PATCH /admin/users/{id}/role)
# -----------------------------------------------------------------
def test_update_role_success_admin_promotes_user_to_admin(monkeypatch):
    _as(ADMIN)  # id=1

    async def fake_find_user_by_id(user_id):
        return _sample_user(id=10, role="USER")

    async def fake_update_role(user_id, role):
        assert user_id == 10
        assert role == "ADMIN"
        return _sample_user(id=10, role="ADMIN")

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)
    monkeypatch.setattr(adminRepository, "updateRole", fake_update_role)

    resp = client.patch("/admin/users/10/role", json={"role": "ADMIN"})

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["role"] == "ADMIN"


def test_update_role_cannot_change_own_role():
    _as(ADMIN)  # id=1

    resp = client.patch("/admin/users/1/role", json={"role": "USER"})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_update_role_admin_cannot_grant_super_admin(monkeypatch):
    _as(ADMIN)  # role=ADMIN, not SUPER_ADMIN

    async def fake_find_user_by_id(user_id):
        return _sample_user(id=10, role="USER")

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)

    resp = client.patch("/admin/users/10/role", json={"role": "SUPER_ADMIN"})

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_update_role_admin_cannot_change_existing_super_admin(monkeypatch):
    _as(ADMIN)

    async def fake_find_user_by_id(user_id):
        return _sample_user(id=10, role="SUPER_ADMIN")

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)

    resp = client.patch("/admin/users/10/role", json={"role": "USER"})

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_update_role_super_admin_can_grant_super_admin(monkeypatch):
    _as(SUPER_ADMIN)  # id=2

    async def fake_find_user_by_id(user_id):
        return _sample_user(id=10, role="ADMIN")

    async def fake_update_role(user_id, role):
        return _sample_user(id=10, role="SUPER_ADMIN")

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)
    monkeypatch.setattr(adminRepository, "updateRole", fake_update_role)

    resp = client.patch("/admin/users/10/role", json={"role": "SUPER_ADMIN"})

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["role"] == "SUPER_ADMIN"


def test_update_role_target_user_not_found(monkeypatch):
    _as(ADMIN)

    async def fake_find_user_by_id(user_id):
        return None

    monkeypatch.setattr(adminRepository, "findUserById", fake_find_user_by_id)

    resp = client.patch("/admin/users/999/role", json={"role": "ADMIN"})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_role_invalid_value_returns_422():
    _as(ADMIN)

    resp = client.patch("/admin/users/10/role", json={"role": "OWNER"})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
