import os
import re
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

_DURATION_PATTERN = re.compile(r"^\s*(\d+)\s*([smhd]?)\s*$", re.IGNORECASE)
_DURATION_UNITS = {"": 1, "s": 1, "m": 60, "h": 60 * 60, "d": 24 * 60 * 60}


def parse_duration(value: str | None, default: timedelta) -> timedelta:
    """
    [만료 시간 문자열 파싱]
    - "3600"(초), "30s", "15m", "1h", "7d" 형태를 timedelta로 변환합니다.
    - 값이 비어 있으면 기본값을 사용하고, 형식이 잘못되었거나 0 이하이면 설정 실수를
      조용히 넘기지 않도록 즉시 ValueError를 발생시킵니다.
    """
    if value is None or not value.strip():
        return default
    match = _DURATION_PATTERN.match(value)
    if not match or int(match.group(1)) <= 0:
        raise ValueError(f"잘못된 만료 시간 형식입니다: {value!r} (예: 3600, 15m, 1h, 7d)")
    return timedelta(seconds=int(match.group(1)) * _DURATION_UNITS[match.group(2).lower()])


JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") or "HS256"
JWT_ACCESS_TOKEN_SECRET = os.getenv("JWT_ACCESS_TOKEN_SECRET")
JWT_REFRESH_TOKEN_SECRET = os.getenv("JWT_REFRESH_TOKEN_SECRET")
ACCESS_TOKEN_COOKIE_NAME = os.getenv("ACCESS_TOKEN_COOKIE_NAME")
REFRESH_TOKEN_COOKIE_NAME = os.getenv("REFRESH_TOKEN_COOKIE_NAME")
JWT_ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES")
JWT_REFRESH_TOKEN_EXPIRES = os.getenv("JWT_REFRESH_TOKEN_EXPIRES")

# 토큰 만료 시간 (JWT exp 클레임과 쿠키 max_age가 모두 이 값을 기준으로 맞춰집니다.)
ACCESS_TOKEN_TTL = parse_duration(JWT_ACCESS_TOKEN_EXPIRES, timedelta(hours=1))
REFRESH_TOKEN_TTL = parse_duration(JWT_REFRESH_TOKEN_EXPIRES, timedelta(days=7))

# 결제 게이트웨이 설정
# - PAYMENT_GATEWAY: "toss"(기본값, 실제 토스페이먼츠 승인 API 호출) 또는 "fake"(로컬 개발/테스트용, 항상 승인)
# - TOSS_PAYMENTS_SECRET_KEY: 토스페이먼츠 시크릿 키 (test_sk_... / live_sk_...)
PAYMENT_GATEWAY = (os.getenv("PAYMENT_GATEWAY") or "toss").strip().lower()
TOSS_PAYMENTS_SECRET_KEY = os.getenv("TOSS_PAYMENTS_SECRET_KEY")
TOSS_PAYMENTS_API_BASE_URL = os.getenv("TOSS_PAYMENTS_API_BASE_URL", "https://api.tosspayments.com")

# 결제 대기(PENDING) 상태로 이 시간(분)만큼 방치된 주문은 자동으로 취소되고 재고가 복구됩니다.
ORDER_PENDING_EXPIRATION_MINUTES = int(os.getenv("ORDER_PENDING_EXPIRATION_MINUTES", "30"))

ENV = {
    "JWT_ALGORITHM": JWT_ALGORITHM,
    "JWT_ACCESS_TOKEN_SECRET": JWT_ACCESS_TOKEN_SECRET,
    "JWT_REFRESH_TOKEN_SECRET": JWT_REFRESH_TOKEN_SECRET,
    "ACCESS_TOKEN_COOKIE_NAME": ACCESS_TOKEN_COOKIE_NAME,
    "REFRESH_TOKEN_COOKIE_NAME": REFRESH_TOKEN_COOKIE_NAME,
    "JWT_ACCESS_TOKEN_EXPIRES": JWT_ACCESS_TOKEN_EXPIRES,
    "JWT_REFRESH_TOKEN_EXPIRES": JWT_REFRESH_TOKEN_EXPIRES,
    "ORDER_PENDING_EXPIRATION_MINUTES": ORDER_PENDING_EXPIRATION_MINUTES,
    "PAYMENT_GATEWAY": PAYMENT_GATEWAY,
}
