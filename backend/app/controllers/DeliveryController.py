from app.services import DeliveryService as deliveryService
from app.types.orderType import DeliveryCreateRequest, DeliveryStatusUpdateRequest


async def createDelivery(body: DeliveryCreateRequest):
    # 배송 등록

    data = await deliveryService.createDelivery(body)
    return {
        "success": True,
        "message": "배송이 등록되었습니다.",
        "data": data,
    }


async def updateDelivery(delivery_id: int, body: DeliveryStatusUpdateRequest):
    # 배송 상태/운송장 정보 변경

    data = await deliveryService.updateDelivery(delivery_id, body)
    return {
        "success": True,
        "message": "배송 정보가 변경되었습니다.",
        "data": data,
    }
