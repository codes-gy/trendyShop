from typing import Optional, Any, Dict
from app.lib.prisma import db as prisma


async def findUserByEmail(email: str) -> Optional[Dict[str, Any]]:
    """
    [이메일로 유저 단일 조회]
    - 서비스 레이어에서 다루기 쉽도록 조회 결과를 dict로 변환하여 리턴합니다.
    """
    user = await prisma.user.find_unique(where={"email": email})
    return user.model_dump() if user else None


async def findUserById(user_id: str) -> Optional[Dict[str, Any]]:
    """
    [ID로 유저 단일 조회]
    """
    user = await prisma.user.find_unique(where={"id": int(user_id)})
    return user.model_dump() if user else None


async def createUser(user_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    [새로운 회원 데이터 생성 (회원가입)]
    - 서비스 단에서 가공된 완벽한 딕셔너리 데이터를 받아 저장합니다.
    """
    new_user = await prisma.user.create(
        data={
            "email": user_dict["email"],
            "password": user_dict.get("password"),
            "name": user_dict["name"],
            "role": user_dict.get("role", "USER"),
            "provider": user_dict.get("provider", "LOCAL"),
            "providerId": user_dict.get("providerId"),
        }
    )
    return new_user.model_dump()


async def updateUser(user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    [회원 데이터 수정 (내 정보 수정)]
    """
    updated_user = await prisma.user.update(
        where={"id": user_id},
        data={
            "email": update_data.get("email"),
            "name": update_data.get("name"),
        }
    )
    return updated_user.model_dump()


# 💡 임시 보관함 가이드 라인 함수 정의 추가 (서비스 레이어 에러 방지 목적)
async def update_refresh_token(user_id: int, refresh_token: str) -> None:
    pass

async def get_refresh_token(user_id: int) -> Optional[str]:
    return None

async def clear_refresh_token(user_id: int) -> None:
    pass