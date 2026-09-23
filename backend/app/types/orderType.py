from datetime import datetime
from typing import Literal

from app.types.authType import UserResponse
from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    """주문서 작성 및 생성 요청 구조"""

    address: str = Field(..., min_length=5, description="정확한 배송지 주소를 입력해주세요.")
    cartItemIds: list[int] = Field(
        ...,
        min_length=1,
        description="주문할 상품 일련번호가 최소 1개 이상 필요합니다.",
    )


class PaymentApproveRequest(BaseModel):
    """외부 PG사(토스, 아임포트 등) 결제 창 인증 성공 후 백엔드 최종 승인 요청 구조"""

    orderId: int
    paymentKey: str = Field(..., description="외부 PG사 거래 식별키")
    amount: int = Field(..., ge=0, description="실제 결제 요청 금액 일치 검증용")
    method: Literal["CARD", "TRANSFER", "VIRTUAL_ACCOUNT", "POINT"]


class OrderItemResponse(BaseModel):
    """주문 스냅샷(이력 보존용 단가 포함) 항목 데이터 반환 스키마"""

    id: int
    productId: int
    price: int
    quantity: int
    totalPrice: int

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """영수증 및 결제 내역 확인 스키마"""

    id: int
    paymentKey: str | None
    method: str
    amount: int
    paidAt: datetime | None
    createdAt: datetime

    class Config:
        from_attributes = True


class DeliveryResponse(BaseModel):
    """실시간 배송 추적 정보 반환 스키마"""

    id: int
    trackingNumber: str | None
    carrier: str | None
    status: Literal["PREPARING", "DISPATCHED", "IN_TRANSIT", "DELIVERED"]
    recipientName: str
    recipientPhone: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """주문 상세 조회/내역 조회를 위한 마스터 응답 스키마 (결제 및 배송 조인)"""

    id: int
    userId: int
    totalPrice: int
    status: Literal["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]
    address: str
    orderItems: list[OrderItemResponse] = []
    payment: PaymentResponse | None = None
    deliveries: list[DeliveryResponse] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class MyPageSummaryResponse(BaseModel):
    """마이페이지 대시보드 통합 정보 스키마"""

    user: UserResponse
    cartItemCount: int
    pendingCount: int
    paidCount: int
    shippedCount: int
    deliveredCount: int

    class Config:
        from_attributes = True
