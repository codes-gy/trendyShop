from datetime import datetime

from app.types.productType import ProductResponse
from pydantic import BaseModel, Field


class CartItemCreateRequest(BaseModel):
    """장바구니 아이템 추가 요청 구조"""

    productId: int
    quantity: int = Field(
        ..., gt=0, description="장바구니 수량은 최소 1개 이상이어야 합니다."
    )


class CartItemUpdateRequest(BaseModel):
    """장바구니 담긴 수량 변경 요청 구조"""

    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    """장바구니 목록 조회 응답 스키마 (연관 상품 상세 포함)"""

    id: int
    userId: int
    productId: int
    quantity: int
    product: ProductResponse | None = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
