from pydantic import BaseModel


class BaseResponse(BaseModel):
    """모든 API 응답의 기본 뼈대가 되는 공통 타입"""

    success: bool
    message: str


class SuccessResponseModel[T](BaseResponse):
    """
    성공 응답 타입
    예: SuccessResponseModel[UserResponse](success=True, message="...", data=user)
    """

    success: bool = True
    data: T | None = None


class ErrorDetails(BaseModel):
    """에러의 세부 정보를 담는 타입"""

    code: str
    message: str


class ErrorResponseModel(BaseResponse):
    """실패/오류 응답 타입"""

    success: bool = False
    error: ErrorDetails


class PaginationMeta(BaseModel):
    """페이징 메타데이터 타입"""

    totalCount: int
    totalPages: int
    currentPage: int
    limit: int
    hasNextPage: bool
    hasPrevPage: bool


class PaginatedData[T](BaseModel):
    """페이징 처리가 된 데이터 구조 타입"""

    items: list[T]
    meta: PaginationMeta


class PaginatedResponseModel[T](BaseResponse):
    """
    최종 페이징 성공 응답 타입
    예: PaginatedResponseModel[UserResponse](data=PaginatedData(...))
    """

    success: bool = True
    data: PaginatedData[T]
