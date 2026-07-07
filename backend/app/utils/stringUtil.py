import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt


def is_empty(value: str | None) -> bool:
    """
    문자열이 비었는지 확인합니다.
    None, 빈 문자열(""), 공백만 있는 문자열("   ")을 모두 빈 값으로 간주합니다.

    :param value: 검사할 문자열 또는 None
    :return: 빈 값일 경우 True, 아닐 경우 False
    """
    if value is None:
        return True
    if not isinstance(value, str):
        return True
    return len(value.strip()) == 0


def normalize_string(value: str | None) -> str | None:
    """
    문자열 정규화 (Normalization)
    문자열이 존재하면 앞뒤 공백을 제거(trim)하여 반환하고, 비어있으면 None을 반환합니다.
    DB 저장 전 데이터를 깔끔하게 정리할 때 유용합니다.

    :param value: 정규화할 문자열 또는 None
    :return: 정제된 문자열 또는 None
    """
    return (
        None if is_empty(value) else value.strip()
    )  # 파이썬의 strip()은 TS의 trim()과 같습니다.


def fallback(a: str | None, b: str) -> str:
    """
    문자열 대체값 반환 (Fallback)
    첫 번째 인자(a)가 비어있을 경우 두 번째 인자(b)를 반환합니다.

    :param a: 우선순위가 높은 문자열 값 (None 가능)
    :param b: a가 비어있을 때 반환할 기본 문자열 값
    :return: a 또는 b
    """
    return b if is_empty(a) else a


def default_value[T](value: T | None, default_val: T) -> T:
    """
    Null 체크 및 기본값 할당 (Generic)
    값이 정확히 None일 경우에만 설정된 기본값을 반환합니다.

    :param value: 검사할 값 (어떤 타입이든 가능)
    :param default_val: 값이 None일 때 반환할 기본값
    :return: 입력값 또는 기본값
    """
    return default_val if value is None else value


def safe_string(value: Any) -> str:
    """
    안전한 문자열 변환기 (Safe Casting)
    어떤 타입의 값이 들어와도 문자열로 안전하게 변환합니다.
    None은 빈 문자열("")로 변환되어 런타임 에러를 방지합니다.

    :param value: 변환할 임의의 값
    :return: 변환된 문자열
    """
    if value is None:
        return ""
    return str(value)


def mask_email(email: str | None) -> str:
    """
    이메일 보안 처리를 위해 앞자리 일부를 마스킹합니다.
    (예: abcdef@gmail.com -> ab****@gmail.com)
    """
    if is_empty(email):
        return ""

    try:
        id_part, domain_part = email.split("@")
        if len(id_part) <= 2:
            masked_id = id_part + "**"
        else:
            masked_id = id_part[:2] + "*" * (len(id_part) - 2)
        return f"{masked_id}@{domain_part}"
    except ValueError:
        return safe_string(email)  # 이메일 형식이 아닐 경우 안전하게 문자열 반환


def escape_like_query(query: str | None) -> str:
    """
    PostgreSQL LIKE 절 검색 시 SQL 특수문자(%, _)를 안전하게 이스케이프합니다.
    prisma.user.find_many(where={"email": {"contains": escape_like_query(search)}}) 형태로 사용합니다.
    """
    if is_empty(query):
        return ""
    # %, _ 앞에 백슬래시(\)를 붙여 단순 문자로 인식하게 만듭니다.
    return query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def to_bool(value: Any) -> bool:
    """
    다양한 형태의 문자열/값('true', '1', 'yes', True)을 정확한 Boolean 값으로 변환합니다.
    대소문자를 구분하지 않습니다.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    return normalized in ("true", "1", "yes", "y", "on")


def extract_bearer_token(header_value: str | None) -> str | None:
    """
    HTTP Authorization 헤더 값에서 'Bearer ' 접두사를 제거하고 순수 JWT 토큰만 추출합니다.
    """
    if is_empty(header_value):
        return None

    if header_value.startswith("Bearer "):
        return header_value[7:].strip()
    if header_value.startswith("bearer "):
        return header_value[7:].strip()

    return header_value.strip()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT 엑세스 토큰을 생성합니다."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    secret_key = os.getenv("JWT_ACCESS_TOKEN_SECRET")
    algorithm = os.getenv("JWT_ALGORITHM")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
