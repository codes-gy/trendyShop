from typing import Any

from app.lib.prisma import db as prisma


def _stripPassword(user: dict[str, Any]) -> dict[str, Any]:
    user.pop("password", None)
    return user


def _buildWhere(keyword: str | None, role: str | None) -> dict[str, Any]:
    where: dict[str, Any] = {}

    if keyword:
        where["OR"] = [
            {"email": {"contains": keyword, "mode": "insensitive"}},
            {"name": {"contains": keyword, "mode": "insensitive"}},
        ]
    if role:
        where["role"] = role

    return where


async def findManyUsers(
    keyword: str | None, role: str | None, page: int, limit: int
) -> tuple[list[dict[str, Any]], int]:
    """
    [전체 회원 목록 조회] (검색/역할 필터/페이지네이션)
    """
    where = _buildWhere(keyword, role)
    skip = (page - 1) * limit

    users = await prisma.user.find_many(
        where=where,
        skip=skip,
        take=limit,
        order={"createdAt": "desc"},
    )
    totalCount = await prisma.user.count(where=where)

    return [_stripPassword(user.model_dump()) for user in users], totalCount


async def findUserById(user_id: int) -> dict[str, Any] | None:
    """
    [회원 단건 조회] (관리자용)
    """
    user = await prisma.user.find_unique(where={"id": user_id})
    return _stripPassword(user.model_dump()) if user else None


async def updateRole(user_id: int, role: str) -> dict[str, Any]:
    """
    [회원 권한 변경]
    """
    updated_user = await prisma.user.update(
        where={"id": user_id},
        data={"role": role},
    )
    return _stripPassword(updated_user.model_dump())
