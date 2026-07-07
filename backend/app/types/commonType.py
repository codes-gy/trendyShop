from pydantic import BaseModel


class BaseResponse(BaseModel):
    """모든 API 응답의 기본 뼈대가 되는 공통 구조"""

    success: bool
    message: str


class SuccessResponseModel[T](BaseResponse):
    """
    단일 데이터 또는 커스텀 객체 반환용 성공 응답 스키마
    예: SuccessResponseModel[UserResponse](message="조회 성공", data=user_obj)
    """

    success: bool = True
    data: T | None = None


class ErrorDetails(BaseModel):
    """에러의 원인을 추적할 수 있는 세부 디버깅 레이어"""

    code: str
    message: str


class ErrorResponseModel(BaseResponse):
    """실패 및 예외 발생 시 표준 응답 스키마"""

    success: bool = False
    error: ErrorDetails


class PaginationMeta(BaseModel):
    """프론트엔드에서 페이지네이션 UI를 그리기 위한 메타데이터"""

    totalCount: int
    totalPages: int
    currentPage: int
    limit: int
    hasNextPage: bool
    hasPrevPage: bool


class PaginatedData[T](BaseModel):
    """페이징 처리가 완료된 결과 데이터 래퍼"""

    items: list[T]
    meta: PaginationMeta


class PaginatedResponseModel[T](BaseResponse):
    """
    리스트/목록 조회 시 표준 페이징 응답 스키마
    예: PaginatedResponseModel[ProductResponse](data=PaginatedData(...))
    """

    success: bool = True
    data: PaginatedData[T]
