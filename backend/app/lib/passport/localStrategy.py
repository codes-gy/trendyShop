from app.repositories import AuthRepository as authRepository
from app.types.authType import LoginRequest
from app.utils.cryptoUtil import verify_password
from fastapi import HTTPException, status
from prisma import Prisma

prisma = Prisma()

async def local_strategy(data : LoginRequest):

    user = await authRepository.findUserByEmail(data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )
    # user_password = user.get("password") if isinstance(user, dict) else getattr(user, "password", None)
    # if not user_password:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="이메일 또는 비밀번호가 잘못되었습니다.",
    #     )

    if user.get("provider") != "LOCAL":

        return user

    if not user.get("password") or not verify_password(data.password, user.get("password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )

    return user
