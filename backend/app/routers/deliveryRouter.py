from typing import Annotated

from app.controllers import DeliveryController as delivery_controller
from app.lib.passport.index import admin_authenticate
from app.types.orderType import DeliveryCreateRequest, DeliveryStatusUpdateRequest
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Delivery"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def createDelivery(
    body: DeliveryCreateRequest,
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await delivery_controller.createDelivery(body)


@router.patch("/{delivery_id}")
async def updateDelivery(
    delivery_id: int,
    body: DeliveryStatusUpdateRequest,
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await delivery_controller.updateDelivery(delivery_id, body)
