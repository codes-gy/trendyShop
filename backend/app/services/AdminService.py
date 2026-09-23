from typing import Any

from app.repositories import AdminRepository as adminRepository
from app.types.authType import RoleUpdateRequest
from fastapi import HTTPException, status


async def listUsers(keyword: str | None, role: str | None, page: int, limit: int) -> dict[str, Any]:
    """
    [전체 회원 목록 조회 서비스] (관리자 전용)
    """
    items, totalCount = await adminRepository.findManyUsers(keyword, role, page, limit)
    totalPages = (totalCount + limit - 1) // limit if totalCount else 0

    return {
        "items": items,
        "meta": {
            "totalCount": totalCount,
            "totalPages": totalPages,
            "currentPage": page,
            "limit": limit,
            "hasNextPage": page < totalPages,
            "hasPrevPage": page > 1,
        },
    }


async def getUser(user_id: int) -> dict[str, Any]:
    """
    [회원 상세 조회 서비스] (관리자 전용)
    """
    user = await adminRepository.findUserById(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 회원입니다.",
        )
    return user


async def updateUserRole(actor: dict[str, Any], target_user_id: int, data: RoleUpdateRequest) -> dict[str, Any]:
    """
    [회원 권한 변경 서비스]
    - 본인의 권한은 스스로 바꿀 수 없습니다.
    - SUPER_ADMIN 권한을 새로 부여하는 것과, 이미 SUPER_ADMIN인 회원의 권한을 바꾸는 것은
      SUPER_ADMIN만 할 수 있습니다. (일반 ADMIN은 USER <-> ADMIN 승격/강등만 가능)
    """
    if target_user_id == actor.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="본인의 권한은 스스로 변경할 수 없습니다.",
        )

    target_user = await getUser(target_user_id)

    actor_is_super_admin = actor.get("role") == "SUPER_ADMIN"

    if data.role == "SUPER_ADMIN" and not actor_is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SUPER_ADMIN 권한 부여는 SUPER_ADMIN만 할 수 있습니다.",
        )

    if target_user["role"] == "SUPER_ADMIN" and not actor_is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SUPER_ADMIN의 권한은 SUPER_ADMIN만 변경할 수 있습니다.",
        )

    return await adminRepository.updateRole(target_user_id, data.role)
