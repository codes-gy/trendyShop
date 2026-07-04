from datetime import UTC, datetime, timedelta, timezone
from typing import Any

# 한국 표준시(KST) 타임존 정의 (+09:00)
KST = timezone(timedelta(hours=9))


def is_valid_date(value: Any) -> bool:
    """
    유효한 datetime 객체인지 확인합니다.
    (파이썬에서는 datetime 인스턴스이면 기본적으로 유효합니다.)
    """
    return isinstance(value, datetime)


def safe_date(value: Any) -> datetime | None:
    """
    주어진 값을 안전하게 datetime 객체로 변환합니다.
    변환에 실패하면 None을 반환합니다.

    :param value: datetime 객체, 타임스탬프(int/float), 또는 날짜 문자열
    :return: 변환된 datetime 객체(기본 UTC 기준) 또는 None
    """
    if value is None:
        return None

    # 1. 이미 datetime 객체인 경우
    if isinstance(value, datetime):
        return value

    # 2. 문자열인 경우 파싱 시도
    if isinstance(value, str):
        cleaned = value.strip()
        if len(cleaned) == 0:
            return None
        try:
            # ISO 8601 포맷 처리 (예: "2023-12-17T02:51:00.000Z")
            # 파이썬 3.11+ 에서는 원본 Z 포맷을 잘 처리하며, 만약의 경우를 위해 replace 처리
            if cleaned.endswith("Z"):
                cleaned = cleaned[:-1] + "+00:00"
            return datetime.fromisoformat(cleaned)
        except ValueError:
            # 일반적인 날짜/시간 포맷 추가 시도
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(cleaned, fmt)
                except ValueError:
                    continue
            return None

    # 3. 타임스탬프(숫자)인 경우 변환 시도
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            # 밀리초(ms) 단위 타임스탬프인 경우 (JS 기본값) 초 단위로 변환
            if value > 1e11:  # 대략 1973년 이후의 밀리초 타임스탬프 기준
                value = value / 1000.0
            return datetime.fromtimestamp(value, tz=UTC)
        except (ValueError, OverflowError):
            return None

    return None


def get_now_iso_string() -> str:
    """
    현재 시간을 ISO 8601 형식 문자열로 반환합니다. (UTC 기준)
    예: "2026-07-05T03:15:00.000000+00:00"
    """
    return datetime.now(UTC).isoformat()


def to_kst(dt: datetime | None) -> datetime | None:
    """
    datetime 객체를 한국 표준시(KST)로 변환합니다.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(KST)


def format_date(value: Any) -> str | None:
    """
    날짜를 'YYYY-MM-DD' 형식의 문자열로 포맷합니다. (KST 한국 시간 기준)
    :param value: 포맷할 날짜 값
    :return: 포맷된 문자열 또는 None
    """
    date_obj = safe_date(value)
    if not date_obj:
        return None

    kst_date = to_kst(date_obj)
    return kst_date.strftime("%Y-%m-%d") if kst_date else None


def format_date_time(value: Any) -> str | None:
    """
    날짜와 시간을 'YYYY-MM-DD HH:mm:ss' 형식의 문자열로 포맷합니다. (KST 한국 시간 기준)
    :param value: 포맷할 날짜 값
    :return: 포맷된 문자열 또는 None
    """
    date_obj = safe_date(value)
    if not date_obj:
        return None

    kst_date = to_kst(date_obj)
    return kst_date.strftime("%Y-%m-%d %H:%M:%S") if kst_date else None


def diff_in_days(start_date: Any, end_date: Any) -> int | None:
    """
    두 날짜 사이의 차이를 일(Day) 단위로 계산합니다.
    (end_date - start_date)

    :return: 두 날짜 사이의 일 수, 유효하지 않으면 None
    """
    start = safe_date(start_date)
    end = safe_date(end_date)

    if not start or not end:
        return None

    # 오차 없는 계산을 위해 타임존 정보 통일 (모두 UTC 기준 혹은 둘 다 모르는 상태로 비교)
    if start.tzinfo is not None:
        start = start.astimezone(UTC)
    else:
        start = start.replace(tzinfo=UTC)

    if end.tzinfo is not None:
        end = end.astimezone(UTC)
    else:
        end = end.replace(tzinfo=UTC)

    time_difference = end - start

    # days 속성을 사용하거나 전체 초를 계산하여 반올림 처리
    return round(time_difference.total_seconds() / (24 * 3600))


def to_relative_time(value: Any) -> str:
    """
    날짜를 "방금 전", "5분 전", "3일 전" 같은 상대적 시간 문자열로 변환합니다.
    """
    dt = safe_date(value)
    if not dt:
        return ""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    now = datetime.now(UTC)
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "방금 전"
    if seconds < 3600:
        return f"{int(seconds // 60)}분 전"
    if seconds < 86400:
        return f"{int(seconds // 3600)}시간 전"
    if seconds < 2592000:  # 30일 이내
        return f"{int(seconds // 86400)}일 전"

    return format_date(dt) or ""
