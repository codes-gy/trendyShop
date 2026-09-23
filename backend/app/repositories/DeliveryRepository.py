from typing import Any

from app.lib.prisma import db as prisma


async def create(
    order_id: int,
    carrier: str,
    tracking_number: str,
    recipient_name: str,
    recipient_phone: str,
) -> dict[str, Any]:
    """
    [배송 등록] (초기 상태는 PREPARING)
    """
    delivery = await prisma.delivery.create(
        data={
            "orderId": order_id,
            "carrier": carrier,
            "trackingNumber": tracking_number,
            "recipientName": recipient_name,
            "recipientPhone": recipient_phone,
        }
    )
    return delivery.model_dump()


async def findById(delivery_id: int) -> dict[str, Any] | None:
    """
    [배송 단건 조회]
    """
    delivery = await prisma.delivery.find_unique(where={"id": delivery_id})
    return delivery.model_dump() if delivery else None


async def findAllByOrder(order_id: int) -> list[dict[str, Any]]:
    """
    [주문에 연결된 모든 배송 건 조회]
    - 주문 전체 배송 완료 여부 판단(부분 배송 등)에 사용됩니다.
    """
    deliveries = await prisma.delivery.find_many(where={"orderId": order_id})
    return [delivery.model_dump() for delivery in deliveries]


async def update(delivery_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    [배송 상태/운송장 정보 부분 수정]
    """
    update_data = {key: value for key, value in data.items() if value is not None}

    updated_delivery = await prisma.delivery.update(
        where={"id": delivery_id},
        data=update_data,
    )
    return updated_delivery.model_dump()
