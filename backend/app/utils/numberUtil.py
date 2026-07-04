import math
from typing import Any


def is_numeric(value: Any) -> bool:
    """
    값이 유효한 숫자인지 확인합니다.
    None, NaN, Infinity, 문자열 등은 유효하지 않은 값(False)으로 처리합니다.
    정수(int)와 실수(float) 타입만 유효한 숫자로 간주합니다.

    :param value: 검사할 값
    :return: 유효한 숫자(int 또는 float)이고 유한한 값이면 True
    """
    # bool 타입은 파이썬에서 int의 서브클래스(True=1, False=0)이므로 명시적으로 제외
    if isinstance(value, bool):
        return False

    if isinstance(value, (int, float)):
        # math.isfinite는 NaN이나 Infinity가 아닐 때 True를 반환합니다.
        return math.isfinite(value)

    return False


def safe_number(value: Any, default_val: float | int = 0) -> float | int:
    """
    값을 안전하게 숫자로 반환합니다. (이미 숫자 타입인 경우 그대로 반환)
    만약 문자열(예: "123")이 들어온 경우 변환을 시도하고, 변환에 실패하면 기본값을 반환합니다.

    :param value: 변환하거나 검사할 값
    :param default_val: 변환 실패 시 반환할 기본값 (기본값: 0)
    :return: 변환된 숫자 또는 기본값
    """
    if is_numeric(value):
        return value

    # 문자열로 된 숫자가 들어오는 경우를 위한 방어 코드 (Casting 지원)
    if isinstance(value, str):
        try:
            # 먼저 정수로 변환 시도
            if value.isdigit():
                return int(value)
            # 소수점이 포함된 문자열인 경우 실수로 변환 시도
            return float(value)
        except ValueError:
            return default_val

    return default_val


def is_positive(value: Any) -> bool:
    """
    값이 양수(0보다 큼)인지 확인합니다.
    유효한 숫자가 아니면 False를 반환합니다.

    :param value: 검사할 값
    :return: 양수이면 True
    """
    # 숫자가 아니면 안전하게 float('-inf')를 주어 0보다 작게 만듭니다.
    return safe_number(value, default_val=float("-inf")) > 0


def is_integer(value: Any) -> bool:
    """
    값이 정수(Integer)인지 확인합니다. (예: 10은 True, 10.5는 False)

    :param value: 검사할 값
    :return: 정수이면 True
    """
    if isinstance(value, bool):
        return False
    # float 타입이더라도 10.0 처럼 정수로 떨어지면 True를 반환할 수 있도록 isinstance와 math.isnan 검증을 거칩니다.
    num = safe_number(value, default_val=float("nan"))
    if math.isnan(num):
        return False

    if isinstance(num, int):
        return True
    return num.is_integer()


def format_number(value: Any, style: str = "decimal") -> str:
    """
    숫자를 지정된 형식으로 포맷합니다. (기본 3자리 콤마 처리)

    :param value: 포맷할 숫자 또는 문자열
    :param style: 포맷 스타일 ('decimal', 'percent')
    :return: 포맷된 문자열
    """
    num = safe_number(value, 0)

    try:
        if style == "percent":
            # 0.123 -> "12.30%"
            return f"{num * 100:.2f}%"

        # 기본 'decimal' 스타일: 천 단위 콤마 추가 (예: 1234567 -> "1,234,567")
        if isinstance(num, int):
            return f"{num:,}"
        else:
            # 실수형인 경우 소수점 둘째 자리까지 표현하되 콤마 적용
            return f"{num:,.2f}"
    except Exception as e:
        # 로그 라이브러리가 있다면 로깅 처리
        print(f"숫자 포맷 오류: {e}")
        return str(num)


def format_currency(value: Any) -> str:
    """
    숫자를 대한민국 원화(KRW) 형식으로 포맷합니다.
    소수점은 버림 처리합니다.

    :param value: 포맷할 숫자
    :return: 예: "1,234,567원"
    """
    num = int(safe_number(value, 0))  # 통화 표현을 위해 정수형으로 강제 변환
    formatted = f"{num:,}"
    return f"{formatted}원"


def calculate_total_pages(total_count: Any, limit: Any) -> int:
    """
    전체 아이템 개수와 페이지당 노출 개수(limit)를 바탕으로 총 페이지 수를 계산합니다.
    (예: 총 21개, limit 10개 -> 3페이지)
    """
    count = max(0, int(safe_number(total_count, 0)))
    page_limit = max(1, int(safe_number(limit, 10)))  # limit이 0이 되는 것을 방지

    # 올림(ceil) 처리를 통해 총 페이지 수 도출
    return math.ceil(count / page_limit)
