from datetime import UTC, datetime

import jwt
from app.lib.token import generateTokens, hashToken, verifyRefreshToken
from app.repositories import AuthRepository as authRepository
from app.types.authType import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
)
from app.utils.cryptoUtil import hash_password
from fastapi import HTTPException, status


async def signup(user_data: SignupRequest) -> dict:
    """
    [회원가입 서비스]
    """
    # 1. 이메일 중복 체크
    existing_user = await authRepository.findUserByEmail(user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 이메일입니다.")

    # 2. 저장할 필드를 명시적으로 골라 담습니다. (role 등 권한 관련 값은 절대 클라이언트 입력을 쓰지 않습니다.)
    user_dict = {
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "name": user_data.name,
        "provider": "LOCAL",
    }

    # 3. 데이터 저장 지시 (레포지토리가 딕셔너리를 받도록 규격화)
    new_user = await authRepository.createUser(user_dict)

    # 4. 패스워드 필드 제거 후 반환
    if "password" in new_user:
        del new_user["password"]

    return new_user


async def login(user: LoginRequest) -> TokenResponse:
    """
    [이메일/비밀번호 로그인 서비스]
    """
    # local_authenticate에서 이메일/비밀번호 검증을 마친 유저(dict)가 넘어옵니다.
    data = generateTokens(user.get("id"))

    # 리프레시 토큰은 해시로 저장해 두고, 재발급/로그아웃 시 이 레코드로 유효성을 판단합니다.
    await authRepository.saveRefreshToken(
        user.get("id"), hashToken(data["refreshToken"]), data["refreshTokenExpiresAt"]
    )

    return {
        "accessToken": data.get("accessToken"),
        "refreshToken": data.get("refreshToken"),
    }


async def readMe(user_id: int) -> dict:
    """
    [내 정보 조회 서비스]
    """
    # 💡 수정: 정확한 레포지토리 함수명으로 변경 (auth_repository -> authRepository)
    user = await authRepository.findUserById(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 회원 정보입니다.")

    if "password" in user:
        del user["password"]

    return user


async def updateMe(user_id: int, update_data: dict) -> dict:
    """
    [내 정보 수정 서비스]
    """
    current_user = await authRepository.findUserById(user_id)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다.")

    if current_user.get("email") != update_data.get("email"):
        email_check = await authRepository.findUserByEmail(update_data.get("email"))
        if email_check:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용 중인 이메일 주소입니다.")

    # 2. 리포지토리에 업데이트 요청 (딕셔너리를 그대로 넘겨줌)
    updated_user = await authRepository.updateUser(user_id, update_data)

    if "password" in updated_user:
        del updated_user["password"]

    return updated_user


async def logout(user_id: int) -> None:
    """
    [로그아웃 서비스]
    - 해당 유저의 활성 리프레시 토큰을 모두 폐기합니다. (이후 /auth/refresh로 재발급 불가)
    - Access Token은 서버에 상태를 두지 않는 JWT라, 이미 발급된 토큰은 만료 시각
      (JWT_ACCESS_TOKEN_EXPIRES, 기본 1시간)까지 유효하다는 한계가 있습니다.
    """
    await authRepository.revokeAllRefreshTokens(user_id)


_INVALID_REFRESH_TOKEN_DETAIL = "만료되었거나 유효하지 않은 토큰입니다. 다시 로그인해주세요."


async def refreshToken(refresh_token: str) -> dict:
    """
    [토큰 재발급 서비스 (리프레시 토큰 회전)]
    1. JWT 서명/만료 검증
    2. DB에 저장된 토큰인지, 폐기/만료되지 않았는지 확인
    3. 기존 토큰을 폐기하고 새 토큰 쌍을 발급 (한 번 쓴 리프레시 토큰은 다시 쓸 수 없음)
    - 이미 폐기된 토큰이 다시 들어오면 탈취 후 재사용으로 간주하고, 해당 유저의 모든 리프레시 토큰을 폐기합니다.
    """
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_REFRESH_TOKEN_DETAIL)

    try:
        payload = verifyRefreshToken(refresh_token)
    except jwt.PyJWTError:
        raise invalid from None

    user_id = payload.get("userId") or payload.get("sub")
    record = await authRepository.findRefreshTokenByHash(hashToken(refresh_token))
    if not record or str(record["userId"]) != str(user_id):
        raise invalid

    if record.get("revokedAt") is not None:
        # 이미 회전/로그아웃으로 폐기된 토큰의 재사용 → 탈취 가능성이 있으므로 전체 세션 폐기
        await authRepository.revokeAllRefreshTokens(record["userId"])
        raise invalid

    if record["expiresAt"] <= datetime.now(UTC):
        raise invalid

    new_tokens = generateTokens(record["userId"])
    rotated = await authRepository.rotateRefreshToken(
        record["id"],
        record["userId"],
        hashToken(new_tokens["refreshToken"]),
        new_tokens["refreshTokenExpiresAt"],
    )
    if not rotated:
        # 동시에 같은 토큰으로 재발급 요청이 들어와 다른 요청이 먼저 회전시킨 경우
        raise invalid

    return {
        "accessToken": new_tokens["accessToken"],
        "refreshToken": new_tokens["refreshToken"],
    }
