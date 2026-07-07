from typing import Annotated

from app.controllers import AuthController as auth_controller
from app.lib.passport.index import jwt_authenticate, local_authenticate
from app.types.authType import (
    SignupRequest,
    TokenRefreshRequest,
    UserResponse,
)
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(
    user: Annotated[dict, Depends(local_authenticate)]
):
    return await auth_controller.login(user)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register(body: SignupRequest):
    return await auth_controller.signup(body)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[dict, Depends(jwt_authenticate)]):
    return await auth_controller.readMe(user)


@router.patch("/updateMe")
async def updateMe(body : dict, user: Annotated[dict, Depends(jwt_authenticate)]):
    return await auth_controller.updateMe(user, body)

@router.post("/logout" )
async def logout(user: Annotated[dict, Depends(jwt_authenticate)]):
    return await auth_controller.logout(user)

@router.post("/refresh" )
async def refresh(body: TokenRefreshRequest):
    return await auth_controller.refresh(body)
