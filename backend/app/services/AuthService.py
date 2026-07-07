import jwt
from fastapi import HTTPException, status
from app.utils.cryptoUtil import hash_password, verify_password
from app.lib.token import generateTokens, verifyAccessToken, verifyRefreshToken
from app.repositories import AuthRepository as authRepository
from app.types.authType import SignupRequest, LoginRequest, UpdateMeRequest, TokenResponse
from app.lib.token import generateTokens

async def signup(user_data: SignupRequest) -> dict:
    """
    [회원가입 서비스]
    """
    # 1. 이메일 중복 체크
    existing_user = await authRepository.findUserByEmail(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 이메일입니다."
        )

    # 2. 로컬 가입인 경우 비밀번호 해싱
    user_dict = user_data.model_dump()
    if user_dict["provider"] == "LOCAL" and user_dict["password"]:
        user_dict["password"] = hash_password(user_dict["password"])

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
    # 1. 가입된 유저인지 조회 (레포지토리가 딕셔너리를 반환함)
    data = generateTokens(user.get("id"))

    return {
        "access_token": data.get("accessToken"),
        "refresh_token": data.get("refreshToken"),
    }


async def readMe(user_id: int) -> dict:
    """
    [내 정보 조회 서비스]
    """
    # 💡 수정: 정확한 레포지토리 함수명으로 변경 (auth_repository -> authRepository)
    user = await authRepository.findUserById(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 회원 정보입니다."
        )
    
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일 주소입니다."
            )

    # 2. 리포지토리에 업데이트 요청 (딕셔너리를 그대로 넘겨줌)
    updated_user = await authRepository.updateUser(user_id, update_data)
    
    if "password" in updated_user:
        del updated_user["password"]
        
    return updated_user


async def logout(user_id: int) -> None:
    """
    [로그아웃 서비스]
    """
    await authRepository.clear_refresh_token(user_id)


async def refreshToken(refresh_token: str) -> dict:
    """
    [토큰 재발급 서비스]
    """
    try:
        payload = verifyRefreshToken(refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="만료되었거나 유효하지 않은 토큰입니다. 다시 로그인해주세요."
        )

    user_id = payload.get("sub")

    
    new_tokens = generateTokens(user_id)
    
    return new_tokens