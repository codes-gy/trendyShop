from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProductSearchQuery(BaseModel):
    """상품 목록 조회 및 필터링/정렬용 쿼리 스트링 명세"""

    keyword: str | None = None
    minPrice: int | None = Field(None, gte=0)
    maxPrice: int | None = Field(None, gte=0)
    isAvailableOnly: bool = False
    sortBy: Literal["createdAt", "priceAsc", "priceDesc"] = "createdAt"
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class ProductImageResponse(BaseModel):
    """상품 이미지 엔티티 반환 구조"""

    id: int
    imageUrl: str
    isMain: bool

    class Config:
        from_attributes = True


class ProductCreateRequest(BaseModel):
    """[관리자] 상품 신규 등록 요청 구조"""

    name: str = Field(..., min_length=1)
    description: str | None = None
    price: int = Field(..., gte=0, description="상품 가격은 0원 이상이어야 합니다.")
    stock: int = Field(..., gte=0, description="최초 재고는 0개 이상이어야 합니다.")


class ProductResponse(BaseModel):
    """상품 정보 상세 반환 스키마 (이미지 배열 포함)"""

    id: int
    name: str
    description: str | None
    price: int
    stock: int
    isAvailable: bool
    images: list[ProductImageResponse] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
