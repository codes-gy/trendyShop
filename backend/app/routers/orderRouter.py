from typing import Annotated

from app.controllers import OrderController as order_controller
from app.lib.passport.index import jwt_authenticate
from app.types.orderType import OrderCreateRequest, PaymentApproveRequest
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Order"])

_ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}


@router.get("")
async def listOrders(user: Annotated[dict, Depends(jwt_authenticate)]):
    return await order_controller.listOrders(user.get("id"))


@router.get("/{order_id}")
async def getOrder(
    order_id: int,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await order_controller.getOrder(user.get("id"), order_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def createOrder(
    body: OrderCreateRequest,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await order_controller.createOrder(user.get("id"), body)


@router.post("/payment")
async def approvePayment(
    body: PaymentApproveRequest,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await order_controller.approvePayment(user.get("id"), body)


@router.patch("/{order_id}/cancel")
async def cancelOrder(
    order_id: int,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    is_admin = user.get("role") in _ADMIN_ROLES
    return await order_controller.cancelOrder(user.get("id"), order_id, is_admin)
