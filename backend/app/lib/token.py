import os
from datetime import UTC, datetime, timedelta

import jwt
from app.lib.env import (
    ACCESS_TOKEN_COOKIE_NAME,
    JWT_ACCESS_TOKEN_SECRET,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_SECRET,
    REFRESH_TOKEN_COOKIE_NAME,
)
from fastapi import Response


def generateTokens(userId : str) -> dict:

    now = datetime.now(UTC)
    access_payload = {
        "sub": str(userId), # 표준 JWT 스펙에 맞춰 id 대신 sub(Subject)를 흔히 사용합니다.
        "id": userId,       # 기존 코드 호환용 id 추가
        "exp": now + timedelta(hours=1)
    }
    refresh_payload = {
        "sub": str(userId),
        "id": userId,
        "exp": now + timedelta(days=1)
    }
    accessToken = jwt.encode(access_payload, JWT_ACCESS_TOKEN_SECRET, algorithm=JWT_ALGORITHM)
    refreshToken = jwt.encode(refresh_payload, JWT_REFRESH_TOKEN_SECRET, algorithm=JWT_ALGORITHM)
    return {
        "accessToken" : accessToken,
        "refreshToken" : refreshToken
    }

def setTokenCookies(res : Response, accessToken : str, refreshToken : str) -> None:
    ONE_HOUR = 60 * 60
    SEVEN_DAYS = 7 * 24 * 60 * 60
    is_production = os.getenv("NODE_ENV") == "production"
    cookie_options = {
        "httponly": True,
        "secure": is_production,
        "samesite": "none" if is_production else "lax",
    }
    res.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=accessToken,
        max_age=ONE_HOUR,
        **cookie_options
    )
    res.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refreshToken,
        max_age=SEVEN_DAYS,
        path="/auth/refresh",
        **cookie_options
    )

def clearTokenCookies(res : Response) -> None:
    res.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME)
    res.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/auth/refresh")

def verifyAccessToken(accessToken : str) -> dict:

    decoded = dict(jwt.decode(
        accessToken,
        JWT_ACCESS_TOKEN_SECRET,
        algorithms=[JWT_ALGORITHM]
    ))
    return {
        "userId" : decoded.get("id"),
    }
def verifyRefreshToken(refreshToken: str) -> dict:
    decoded = dict(jwt.decode(refreshToken, JWT_REFRESH_TOKEN_SECRET, algorithms=[JWT_ALGORITHM]))
    return {
        "userId": decoded.get("id"),
        "sub": decoded.get("sub")
    }
