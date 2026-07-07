import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.repositories import AuthRepository as authRepository
from app.lib.env import JWT_ALGORITHM, JWT_ACCESS_TOKEN_SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def jwt_strategy(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 토큰이 유효하지 않거나 만료되었습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_ACCESS_TOKEN_SECRET, algorithms=[JWT_ALGORITHM])
        
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
        
    except jwt.PyJWTError:
        raise credentials_exception

    user = await authRepository.findUserById(userId)
    if not user:
        raise credentials_exception

    return user
