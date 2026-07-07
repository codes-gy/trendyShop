from datetime import datetime

from app.types.authType import UserResponse
from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """상품 리뷰 작성 요청 구조"""

    productId: int
    rating: int = Field(
        ..., ge=1, le=5, description="별점은 1점부터 5점까지만 허용됩니다."
    )
    comment: str = Field(
        ..., min_length=5, description="최소 5자 이상의 생생한 후기를 남겨주세요."
    )


class ReviewResponse(BaseModel):
    """상품 상세 화면 하단이나 마이페이지 리뷰 목록 노출 스키마"""

    id: int
    userId: int
    productId: int
    rating: int
    comment: str
    user: UserResponse | None = None  # 리뷰어 정보 포함
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
