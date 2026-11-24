from datetime import UTC, datetime
from typing import Any

from app.lib.prisma import db as prisma


async def findUserByEmail(email: str) -> dict[str, Any] | None:
    """
    [이메일로 유저 단일 조회]
    - 서비스 레이어에서 다루기 쉽도록 조회 결과를 dict로 변환하여 리턴합니다.
    """
    user = await prisma.user.find_unique(where={"email": email})
    return user.model_dump() if user else None


async def findUserById(user_id: str) -> dict[str, Any] | None:
    """
    [ID로 유저 단일 조회]
    """
    user = await prisma.user.find_unique(where={"id": int(user_id)})
    return user.model_dump() if user else None


async def createUser(user_dict: dict[str, Any]) -> dict[str, Any]:
    """
    [새로운 회원 데이터 생성 (회원가입)]
    - 서비스 단에서 가공된 완벽한 딕셔너리 데이터를 받아 저장합니다.
    """
    new_user = await prisma.user.create(
        data={
            "email": user_dict["email"],
            "password": user_dict.get("password"),
            "name": user_dict["name"],
            # 권한은 클라이언트 입력과 무관하게 항상 기본 권한(USER)으로 생성합니다.
            # (관리자 권한 부여는 /admin/users/{id}/role 에서만 가능합니다.)
            "role": "USER",
            "provider": user_dict.get("provider", "LOCAL"),
            "providerId": user_dict.get("providerId"),
        }
    )
    return new_user.model_dump()


async def updateUser(user_id: int, update_data: dict[str, Any]) -> dict[str, Any]:
    """
    [회원 데이터 수정 (내 정보 수정)]
    """
    updated_user = await prisma.user.update(
        where={"id": user_id},
        data={
            "email": update_data.get("email"),
            "name": update_data.get("name"),
        },
    )
    return updated_user.model_dump()


# -----------------------------------------------------------------
# 리프레시 토큰 저장소 (RefreshToken 테이블)
# - 토큰 원문은 저장하지 않고 SHA-256 해시(tokenHash)만 저장합니다.
# -----------------------------------------------------------------
async def saveRefreshToken(user_id: int, token_hash: str, expires_at: datetime) -> None:
    """[로그인 시 발급한 리프레시 토큰 저장]"""
    await prisma.refreshtoken.create(
        data={
            "userId": int(user_id),
            "tokenHash": token_hash,
            "expiresAt": expires_at,
        }
    )


async def findRefreshTokenByHash(token_hash: str) -> dict[str, Any] | None:
    """[해시로 리프레시 토큰 레코드 조회]"""
    record = await prisma.refreshtoken.find_unique(where={"tokenHash": token_hash})
    return record.model_dump() if record else None


async def rotateRefreshToken(old_token_id: int, user_id: int, new_token_hash: str, new_expires_at: datetime) -> bool:
    """
    [리프레시 토큰 회전 트랜잭션]
    - 기존 토큰을 "아직 폐기되지 않은 경우에만" 폐기(compare-and-set)하고 새 토큰을 저장합니다.
    - 동시에 같은 토큰으로 두 번 재발급을 요청하면 한쪽만 성공하고, 나머지는 False를 받습니다.
    """
    async with prisma.tx() as transaction:
        revoked_count = await transaction.refreshtoken.update_many(
            where={"id": old_token_id, "revokedAt": None},
            data={"revokedAt": datetime.now(UTC)},
        )
        if revoked_count != 1:
            return False

        await transaction.refreshtoken.create(
            data={
                "userId": int(user_id),
                "tokenHash": new_token_hash,
                "expiresAt": new_expires_at,
            }
        )
    return True


async def revokeAllRefreshTokens(user_id: int) -> int:
    """[해당 유저의 활성 리프레시 토큰 전체 폐기] (로그아웃, 토큰 재사용 탐지 시)"""
    return await prisma.refreshtoken.update_many(
        where={"userId": int(user_id), "revokedAt": None},
        data={"revokedAt": datetime.now(UTC)},
    )
