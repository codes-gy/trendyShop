from typing import Any

from app.repositories import DeliveryRepository as deliveryRepository
from app.repositories import OrderRepository as orderRepository
from app.types.orderType import DeliveryCreateRequest, DeliveryStatusUpdateRequest
from fastapi import HTTPException, status

_SHIPPED_TRIGGER_STATUSES = {"DISPATCHED", "IN_TRANSIT"}


async def createDelivery(data: DeliveryCreateRequest) -> dict[str, Any]:
    """
    [배송 등록 서비스] (관리자 전용)
    - 결제가 완료(PAID)된 주문에 대해서만 배송을 등록할 수 있습니다.
    """
    order = await orderRepository.findById(data.orderId)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 주문입니다.",
        )
    if order["status"] != "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="결제가 완료된 주문에만 배송을 등록할 수 있습니다.",
        )

    return await deliveryRepository.create(
        order_id=data.orderId,
        carrier=data.carrier,
        tracking_number=data.trackingNumber,
        recipient_name=data.recipientName,
        recipient_phone=data.recipientPhone,
    )


async def updateDelivery(delivery_id: int, data: DeliveryStatusUpdateRequest) -> dict[str, Any]:
    """
    [배송 상태/운송장 정보 변경 서비스] (관리자 전용)
    - 배송 상태에 따라 연결된 주문의 상태도 함께 동기화합니다.
      (DISPATCHED/IN_TRANSIT -> 주문 SHIPPED, 모든 배송건 DELIVERED -> 주문 DELIVERED)
    """
    delivery = await deliveryRepository.findById(delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 배송 건입니다.",
        )

    updated_delivery = await deliveryRepository.update(delivery_id, data.model_dump())

    if data.status in _SHIPPED_TRIGGER_STATUSES:
        await orderRepository.updateStatus(delivery["orderId"], "SHIPPED")
    elif data.status == "DELIVERED":
        all_deliveries = await deliveryRepository.findAllByOrder(delivery["orderId"])
        if all(d["status"] == "DELIVERED" for d in all_deliveries):
            await orderRepository.updateStatus(delivery["orderId"], "DELIVERED")

    return updated_delivery
