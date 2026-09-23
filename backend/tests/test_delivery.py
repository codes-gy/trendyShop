import pytest
from app.lib.passport.roleGuard import require_admin
from app.main import app
from app.repositories import DeliveryRepository as deliveryRepository
from app.repositories import OrderRepository as orderRepository
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

ADMIN_USER = {"id": 1, "email": "admin@test.com", "role": "ADMIN"}


def _sample_order(**overrides) -> dict:
    base = {"id": 1, "userId": 1, "status": "PAID", "totalPrice": 20000}
    base.update(overrides)
    return base


def _sample_delivery(**overrides) -> dict:
    base = {
        "id": 1,
        "orderId": 1,
        "trackingNumber": "123456789",
        "carrier": "CJ대한통운",
        "status": "PREPARING",
        "recipientName": "홍길동",
        "recipientPhone": "010-1234-5678",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _as_admin():
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER


VALID_CREATE_BODY = {
    "orderId": 1,
    "carrier": "CJ대한통운",
    "trackingNumber": "123456789",
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
}


# -----------------------------------------------------------------
# 배송 등록 (POST /deliveries)
# -----------------------------------------------------------------
def test_create_delivery_requires_authentication():
    resp = client.post("/deliveries", json=VALID_CREATE_BODY)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_delivery_success(monkeypatch):
    _as_admin()

    async def fake_order_find_by_id(order_id):
        return _sample_order(id=1, status="PAID")

    async def fake_create(**kwargs):
        assert kwargs["order_id"] == 1
        assert kwargs["carrier"] == "CJ대한통운"
        return _sample_delivery()

    monkeypatch.setattr(orderRepository, "findById", fake_order_find_by_id)
    monkeypatch.setattr(deliveryRepository, "create", fake_create)

    resp = client.post("/deliveries", json=VALID_CREATE_BODY)

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["data"]["status"] == "PREPARING"


def test_create_delivery_order_not_found(monkeypatch):
    _as_admin()

    async def fake_order_find_by_id(order_id):
        return None

    monkeypatch.setattr(orderRepository, "findById", fake_order_find_by_id)

    resp = client.post("/deliveries", json=VALID_CREATE_BODY)

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_create_delivery_order_not_paid(monkeypatch):
    _as_admin()

    async def fake_order_find_by_id(order_id):
        return _sample_order(id=1, status="PENDING")

    monkeypatch.setattr(orderRepository, "findById", fake_order_find_by_id)

    resp = client.post("/deliveries", json=VALID_CREATE_BODY)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


# -----------------------------------------------------------------
# 배송 상태 변경 (PATCH /deliveries/{id})
# -----------------------------------------------------------------
def test_update_delivery_not_found(monkeypatch):
    _as_admin()

    async def fake_find_by_id(delivery_id):
        return None

    monkeypatch.setattr(deliveryRepository, "findById", fake_find_by_id)

    resp = client.patch("/deliveries/999", json={"status": "DISPATCHED"})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_delivery_to_dispatched_syncs_order_to_shipped(monkeypatch):
    _as_admin()

    async def fake_find_by_id(delivery_id):
        return _sample_delivery(id=1, orderId=1, status="PREPARING")

    async def fake_update(delivery_id, data):
        return _sample_delivery(id=1, status="DISPATCHED")

    order_status_calls = []

    async def fake_update_order_status(order_id, order_status):
        order_status_calls.append((order_id, order_status))
        return _sample_order(id=order_id, status=order_status)

    monkeypatch.setattr(deliveryRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(deliveryRepository, "update", fake_update)
    monkeypatch.setattr(orderRepository, "updateStatus", fake_update_order_status)

    resp = client.patch("/deliveries/1", json={"status": "DISPATCHED"})

    assert resp.status_code == status.HTTP_200_OK
    assert order_status_calls == [(1, "SHIPPED")]


def test_update_delivery_to_delivered_syncs_order_when_all_delivered(monkeypatch):
    _as_admin()

    async def fake_find_by_id(delivery_id):
        return _sample_delivery(id=1, orderId=1, status="IN_TRANSIT")

    async def fake_update(delivery_id, data):
        return _sample_delivery(id=1, status="DELIVERED")

    async def fake_find_all_by_order(order_id):
        # 이 주문에는 배송건이 하나뿐이고, 이제 막 DELIVERED로 바뀜
        return [_sample_delivery(id=1, orderId=order_id, status="DELIVERED")]

    order_status_calls = []

    async def fake_update_order_status(order_id, order_status):
        order_status_calls.append((order_id, order_status))
        return _sample_order(id=order_id, status=order_status)

    monkeypatch.setattr(deliveryRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(deliveryRepository, "update", fake_update)
    monkeypatch.setattr(deliveryRepository, "findAllByOrder", fake_find_all_by_order)
    monkeypatch.setattr(orderRepository, "updateStatus", fake_update_order_status)

    resp = client.patch("/deliveries/1", json={"status": "DELIVERED"})

    assert resp.status_code == status.HTTP_200_OK
    assert order_status_calls == [(1, "DELIVERED")]


def test_update_delivery_to_delivered_waits_for_other_deliveries(monkeypatch):
    _as_admin()

    async def fake_find_by_id(delivery_id):
        return _sample_delivery(id=1, orderId=1, status="IN_TRANSIT")

    async def fake_update(delivery_id, data):
        return _sample_delivery(id=1, status="DELIVERED")

    async def fake_find_all_by_order(order_id):
        # 같은 주문에 아직 배송 중인 다른 배송건이 남아있음 (부분 배송 완료)
        return [
            _sample_delivery(id=1, orderId=order_id, status="DELIVERED"),
            _sample_delivery(id=2, orderId=order_id, status="IN_TRANSIT"),
        ]

    order_status_calls = []

    async def fake_update_order_status(order_id, order_status):
        order_status_calls.append((order_id, order_status))
        return _sample_order(id=order_id, status=order_status)

    monkeypatch.setattr(deliveryRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(deliveryRepository, "update", fake_update)
    monkeypatch.setattr(deliveryRepository, "findAllByOrder", fake_find_all_by_order)
    monkeypatch.setattr(orderRepository, "updateStatus", fake_update_order_status)

    resp = client.patch("/deliveries/1", json={"status": "DELIVERED"})

    assert resp.status_code == status.HTTP_200_OK
    assert order_status_calls == []  # 아직 전체 배송 완료가 아니므로 주문 상태는 그대로


def test_update_delivery_tracking_info_only_no_order_sync(monkeypatch):
    _as_admin()

    async def fake_find_by_id(delivery_id):
        return _sample_delivery(id=1, orderId=1, status="PREPARING")

    async def fake_update(delivery_id, data):
        assert data["trackingNumber"] == "999999999"
        return _sample_delivery(id=1, trackingNumber="999999999")

    order_status_calls = []

    async def fake_update_order_status(order_id, order_status):
        order_status_calls.append((order_id, order_status))

    monkeypatch.setattr(deliveryRepository, "findById", fake_find_by_id)
    monkeypatch.setattr(deliveryRepository, "update", fake_update)
    monkeypatch.setattr(orderRepository, "updateStatus", fake_update_order_status)

    resp = client.patch("/deliveries/1", json={"trackingNumber": "999999999"})

    assert resp.status_code == status.HTTP_200_OK
    assert order_status_calls == []
