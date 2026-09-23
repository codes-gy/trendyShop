from typing import Annotated

from app.controllers import AdminController as admin_controller
from app.lib.passport.index import admin_authenticate
from app.types.authType import AdminUserListQuery, RoleUpdateRequest
from fastapi import APIRouter, Depends

router = APIRouter(tags=["Admin"])


@router.get("")
async def listUsers(
    query: Annotated[AdminUserListQuery, Depends()],
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await admin_controller.listUsers(query)


@router.get("/{user_id}")
async def getUser(
    user_id: int,
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await admin_controller.getUser(user_id)


@router.patch("/{user_id}/role")
async def updateUserRole(
    user_id: int,
    body: RoleUpdateRequest,
    admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await admin_controller.updateUserRole(admin, user_id, body)
