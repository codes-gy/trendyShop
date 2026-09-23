from typing import Annotated

from app.controllers import CartController as cart_controller
from app.lib.passport.index import jwt_authenticate
from app.types.cartType import CartItemCreateRequest, CartItemUpdateRequest
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Cart"])


@router.get("")
async def listCart(user: Annotated[dict, Depends(jwt_authenticate)]):
    return await cart_controller.listCart(user.get("id"))


@router.post("", status_code=status.HTTP_201_CREATED)
async def addItem(
    body: CartItemCreateRequest,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await cart_controller.addItem(user.get("id"), body)


@router.patch("/{cart_item_id}")
async def updateItem(
    cart_item_id: int,
    body: CartItemUpdateRequest,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await cart_controller.updateItem(user.get("id"), cart_item_id, body)


@router.delete("/{cart_item_id}")
async def removeItem(
    cart_item_id: int,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await cart_controller.removeItem(user.get("id"), cart_item_id)
