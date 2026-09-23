from typing import Annotated

from app.lib.passport.jwtStrategy import jwt_strategy
from fastapi import Depends, HTTPException, status

ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}


async def require_admin(
    user: Annotated[dict, Depends(jwt_strategy)],
) -> dict:
    """
    [관리자 권한 가드]
    - 로그인(JWT 인증)은 되어 있으나 ADMIN/SUPER_ADMIN 권한이 아니면 403을 반환합니다.
    """
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다.",
        )
    return user
