from app.services import AdminService as adminService
from app.types.authType import AdminUserListQuery, RoleUpdateRequest


async def listUsers(query: AdminUserListQuery):
    # 전체 회원 목록 조회

    data = await adminService.listUsers(query.keyword, query.role, query.page, query.limit)
    return {
        "success": True,
        "message": "회원 목록 조회에 성공했습니다.",
        "data": data,
    }


async def getUser(user_id: int):
    # 회원 상세 조회

    data = await adminService.getUser(user_id)
    return {
        "success": True,
        "message": "회원 조회에 성공했습니다.",
        "data": data,
    }


async def updateUserRole(actor: dict, user_id: int, body: RoleUpdateRequest):
    # 회원 권한 변경

    data = await adminService.updateUserRole(actor, user_id, body)
    return {
        "success": True,
        "message": "회원 권한이 변경되었습니다.",
        "data": data,
    }
