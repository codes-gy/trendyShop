from app.services import AuthService as auth_service
from app.types.authType import (
    LoginRequest,
    SignupRequest,
    TokenRefreshRequest,
    UpdateMeRequest,
)
from fastapi import HTTPException, status


async def signup(user: SignupRequest):
    # 회원가입

    new_user = await auth_service.signup(user)
    return {
        "success": True,
        "message": "회원가입이 성공적으로 완료되었습니다.",
        "data": new_user
    }


async def login(user: LoginRequest):
    # 로그인

    data = await auth_service.login(user)
    return {
        "success": True,
        "message": "로그인에 성공했습니다.",
        "data": data
    }

async def readMe(user: str):
    # 내 정보 조회
    return await auth_service.readMe(user.get("id"))

async def updateMe(data : UpdateMeRequest,user: dict):
    # 내 정보 수정

    if not user or "id" not in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="접근 권한이 없습니다."
        )
    userId = user.get("id")

    new_user = await auth_service.updateMe(userId, data)
    return {
        "success": True,
        "message": "회원가입이 성공적으로 완료되었습니다.",
        "data": new_user
    }

async def logout(data: dict):
    # 로그아웃

   return {"success": True, "message": "로그아웃 되었습니다."}

async def refresh(data: TokenRefreshRequest):
    # 회원가입 비즈니스 로직 호출

    new_token = await auth_service.refreshToken(data.refreshToken)
    return {
        "success": True,
        "message": "토큰이 성공적으로 재발급되었습니다.",
        "data": new_token
    }
