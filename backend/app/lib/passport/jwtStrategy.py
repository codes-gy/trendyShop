import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from prisma import Prisma

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
prisma = Prisma()

SECRET_KEY = os.getenv("JWT_ACCESS_TOKEN_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")


async def jwt_strategy(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 토큰이 유효하지 않거나 만료되었습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await prisma.user.find_unique(where={"email": email})
    if not user:
        raise credentials_exception

    return user
