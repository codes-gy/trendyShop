from app.repositories import AuthRepository as authRepository
from app.types.authType import LoginRequest
from app.utils.cryptoUtil import verify_password
from fastapi import HTTPException, status
from prisma import Prisma

prisma = Prisma()


async def local_strategy(data: LoginRequest):

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

    # 소셜(KAKAO/GOOGLE/NAVER) 계정은 비밀번호가 없으므로 이메일/비밀번호 로그인을 허용하지 않습니다.
    # (기존에는 provider가 LOCAL이 아니면 비밀번호 검증 없이 그대로 로그인되어, 이메일만 알면
    #  소셜 계정을 탈취할 수 있었습니다. 실제 소셜 로그인은 OAuth 연동 후 별도 엔드포인트로 처리해야 합니다.)
    if user.get("provider") != "LOCAL":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )

    if not user.get("password") or not verify_password(data.password, user.get("password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )

    return user
