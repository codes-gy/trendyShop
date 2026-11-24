import hashlib
import os
import uuid
from datetime import UTC, datetime

import jwt
from app.lib.env import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_TTL,
    JWT_ACCESS_TOKEN_SECRET,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_SECRET,
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_TTL,
)
from fastapi import Response

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def generateTokens(userId: str) -> dict:
    """
    [Access/Refresh 토큰 쌍 발급]
    - 만료 시간은 JWT_ACCESS_TOKEN_EXPIRES / JWT_REFRESH_TOKEN_EXPIRES 환경변수(기본 1h / 7d)를 따릅니다.
    - 리프레시 토큰에는 고유 jti를 넣어, 같은 초에 발급되어도 서로 다른 토큰(=다른 해시)이 되도록 합니다.
    - refreshTokenExpiresAt은 DB 저장용이며 클라이언트 응답에는 포함하지 않습니다.
    """
    now = datetime.now(UTC)
    refresh_expires_at = now + REFRESH_TOKEN_TTL
    access_payload = {
        "sub": str(userId),  # 표준 JWT 스펙에 맞춰 id 대신 sub(Subject)를 흔히 사용합니다.
        "id": userId,  # 기존 코드 호환용 id 추가
        "type": ACCESS_TOKEN_TYPE,
        "exp": now + ACCESS_TOKEN_TTL,
    }
    refresh_payload = {
        "sub": str(userId),
        "id": userId,
        "type": REFRESH_TOKEN_TYPE,
        "jti": uuid.uuid4().hex,
        "exp": refresh_expires_at,
    }
    accessToken = jwt.encode(access_payload, JWT_ACCESS_TOKEN_SECRET, algorithm=JWT_ALGORITHM)
    refreshToken = jwt.encode(refresh_payload, JWT_REFRESH_TOKEN_SECRET, algorithm=JWT_ALGORITHM)
    return {
        "accessToken": accessToken,
        "refreshToken": refreshToken,
        "refreshTokenExpiresAt": refresh_expires_at,
    }


def hashToken(token: str) -> str:
    """리프레시 토큰은 원문 대신 SHA-256 해시로만 DB에 저장/조회합니다."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def setTokenCookies(res: Response, accessToken: str, refreshToken: str) -> None:
    is_production = os.getenv("NODE_ENV") == "production"
    cookie_options = {
        "httponly": True,
        "secure": is_production,
        "samesite": "none" if is_production else "lax",
    }
    # 쿠키 만료 시간도 JWT exp와 같은 환경변수 값을 사용해 서로 어긋나지 않게 합니다.
    res.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=accessToken,
        max_age=int(ACCESS_TOKEN_TTL.total_seconds()),
        **cookie_options,
    )
    res.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refreshToken,
        max_age=int(REFRESH_TOKEN_TTL.total_seconds()),
        path="/auth/refresh",
        **cookie_options,
    )


def clearTokenCookies(res: Response) -> None:
    res.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME)
    res.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/auth/refresh")


def verifyAccessToken(accessToken: str) -> dict:
    decoded = dict(jwt.decode(accessToken, JWT_ACCESS_TOKEN_SECRET, algorithms=[JWT_ALGORITHM]))
    if decoded.get("type") == REFRESH_TOKEN_TYPE:
        raise jwt.InvalidTokenError("리프레시 토큰은 액세스 토큰으로 사용할 수 없습니다.")
    return {
        "userId": decoded.get("id"),
    }


def verifyRefreshToken(refreshToken: str) -> dict:
    decoded = dict(jwt.decode(refreshToken, JWT_REFRESH_TOKEN_SECRET, algorithms=[JWT_ALGORITHM]))
    if decoded.get("type") not in (None, REFRESH_TOKEN_TYPE):
        raise jwt.InvalidTokenError("리프레시 토큰이 아닙니다.")
    return {"userId": decoded.get("id"), "sub": decoded.get("sub")}
