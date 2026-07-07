from collections.abc import Mapping
from typing import Any


def omit(data: dict[str, Any], keys_to_remove: list[str]) -> dict[str, Any]:
    """
    딕셔너리에서 특정 키들을 제외한 새로운 딕셔너리를 반환합니다. (TS의 Omit)
    예: omit(user_dict, ["password", "is_deleted"])
    """
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if k not in keys_to_remove}


def pick(data: dict[str, Any], keys_to_keep: list[str]) -> dict[str, Any]:
    """
    딕셔너리에서 특정 키들만 추출한 새로운 딕셔너리를 반환합니다. (TS의 Pick)
    예: pick(user_dict, ["id", "email"])
    """
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if k in keys_to_keep}


def get_nested(data: Mapping[str, Any], path: str, default: Any = None) -> Any:
    """
    점(.)으로 구분된 경로를 통해 중첩된 딕셔너리 값을 안전하게 가져옵니다.
    예: get_nested(profile, "user.settings.theme", "light")
    """
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current
