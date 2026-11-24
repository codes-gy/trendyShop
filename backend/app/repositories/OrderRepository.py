from datetime import UTC, datetime
from typing import Any

from app.lib.prisma import db as prisma


class InsufficientStockError(Exception):
    """주문 트랜잭션 안에서 재고 차감(조건부 UPDATE)이 실패했을 때 발생합니다. (재고 부족/판매 중지/삭제)"""

    def __init__(self, product_id: int):
        super().__init__(f"재고 차감 실패 (productId={product_id})")
        self.product_id = product_id


class OrderStatusConflictError(Exception):
    """주문 상태 전이(compare-and-set)가 실패했을 때 발생합니다. (다른 요청이 먼저 상태를 바꾼 경우)"""

    def __init__(self, order_id: int):
        super().__init__(f"주문 상태가 이미 변경되었습니다. (orderId={order_id})")
        self.order_id = order_id


_INCLUDE_FULL = {
    "orderItems": True,
    "payment": True,
    "deliveries": True,
}


async def findManyByUser(user_id: int) -> list[dict[str, Any]]:
    """
    [내 주문 목록 조회] (주문 상품/결제/배송 정보 포함)
    """
    orders = await prisma.order.find_many(
        where={"userId": user_id},
        include=_INCLUDE_FULL,
        order={"createdAt": "desc"},
    )
    return [order.model_dump() for order in orders]


async def findById(order_id: int) -> dict[str, Any] | None:
    """
    [주문 단건 상세 조회] (소유자 검증은 서비스 레이어에서 처리)
    """
    order = await prisma.order.find_unique(
        where={"id": order_id},
        include=_INCLUDE_FULL,
    )
    return order.model_dump() if order else None


async def createOrderWithItems(
    user_id: int,
    address: str,
    total_price: int,
    order_items: list[dict[str, Any]],
    cart_item_ids: list[int],
) -> dict[str, Any]:
    """
    [주문 생성 트랜잭션]
    - Order + OrderItem 스냅샷 생성, 주문된 상품들의 재고 차감, 체크아웃에 쓰인
      장바구니 아이템 삭제를 하나의 트랜잭션으로 묶어 원자적으로 처리합니다.
      (중간에 하나라도 실패하면 전체가 롤백됩니다.)
    """
    async with prisma.tx() as transaction:
        # 1) 재고 차감: "재고가 충분하고 판매 중인 경우에만" 차감하는 조건부 UPDATE 한 문장으로 처리합니다.
        #    UPDATE "Product" SET stock = stock - :qty WHERE id = :id AND stock >= :qty AND ...
        #    동시에 같은 상품을 주문해도 DB가 행 잠금 후 WHERE 조건을 다시 평가하므로 재고가 음수가 되지 않습니다.
        #    영향받은 행이 0이면 예외를 던져 트랜잭션 전체(이미 차감한 다른 상품 포함)를 롤백합니다.
        for item in order_items:
            updated_count = await transaction.product.update_many(
                where={
                    "id": item["productId"],
                    "stock": {"gte": item["quantity"]},
                    "isAvailable": True,
                    "deletedAt": None,
                },
                data={"stock": {"decrement": item["quantity"]}},
            )
            if updated_count != 1:
                raise InsufficientStockError(item["productId"])

        new_order = await transaction.order.create(
            data={
                "userId": user_id,
                "address": address,
                "totalPrice": total_price,
                "orderItems": {"create": order_items},
            },
            include=_INCLUDE_FULL,
        )

        if cart_item_ids:
            await transaction.cartitem.delete_many(where={"id": {"in": cart_item_ids}, "userId": user_id})

    return new_order.model_dump()


async def updateStatus(order_id: int, order_status: str) -> dict[str, Any]:
    """
    [주문 상태 변경]
    """
    updated = await prisma.order.update(
        where={"id": order_id},
        data={"status": order_status},
        include=_INCLUDE_FULL,
    )
    return updated.model_dump()


async def markPaidWithPayment(order_id: int, payment_key: str, method: str, amount: int) -> dict[str, Any]:
    """
    [결제 완료 처리 트랜잭션]
    - 주문 상태를 PENDING → PAID로 "PENDING인 경우에만" 전환(compare-and-set)하고, 결제 정보를 생성합니다.
    - 두 작업을 하나의 트랜잭션으로 묶어, 둘 중 하나라도 실패하면 함께 롤백됩니다.
    - 그 사이 주문이 만료/취소되었다면 OrderStatusConflictError,
      같은 paymentKey/주문으로 이미 결제가 저장되어 있다면 prisma UniqueViolationError가 발생합니다.
    """
    async with prisma.tx() as transaction:
        updated_count = await transaction.order.update_many(
            where={"id": order_id, "status": "PENDING"},
            data={"status": "PAID"},
        )
        if updated_count != 1:
            raise OrderStatusConflictError(order_id)

        await transaction.payment.create(
            data={
                "orderId": order_id,
                "paymentKey": payment_key,
                "method": method,
                "amount": amount,
                "paidAt": datetime.now(UTC),
            }
        )

        paid_order = await transaction.order.find_unique(where={"id": order_id}, include=_INCLUDE_FULL)

    return paid_order.model_dump()


async def hasPurchasedProduct(user_id: int, product_id: int) -> bool:
    """
    [해당 유저가 이 상품을 구매(결제 완료 이상)한 이력이 있는지 확인]
    - 리뷰 작성 자격 검증에 사용됩니다. (PENDING/CANCELLED 주문은 인정하지 않습니다.)
    """
    order_item = await prisma.orderitem.find_first(
        where={
            "productId": product_id,
            "order": {
                "is": {
                    "userId": user_id,
                    "status": {"in": ["PAID", "SHIPPED", "DELIVERED"]},
                }
            },
        }
    )
    return order_item is not None


async def cancelOrderWithRestock(
    order_id: int,
    order_items: list[dict[str, Any]],
    from_statuses: list[str] | None = None,
) -> dict[str, Any]:
    """
    [주문 취소 트랜잭션]
    - 주문 상태를 "from_statuses(기본 PENDING/PAID) 중 하나인 경우에만" CANCELLED로 전환합니다. (compare-and-set)
    - 상태 전환에 성공한 경우에만 각 주문 아이템 수량만큼 재고를 복구합니다.
      그래서 취소 요청이 동시에 두 번 들어오거나 자동 만료와 겹쳐도 재고가 두 번 복구되지 않습니다.
    - 전환에 실패하면(이미 다른 요청이 취소/배송 처리함) OrderStatusConflictError가 발생합니다.
    """
    statuses = from_statuses or ["PENDING", "PAID"]
    async with prisma.tx() as transaction:
        updated_count = await transaction.order.update_many(
            where={"id": order_id, "status": {"in": statuses}},
            data={"status": "CANCELLED"},
        )
        if updated_count != 1:
            raise OrderStatusConflictError(order_id)

        for item in order_items:
            await transaction.product.update(
                where={"id": item["productId"]},
                data={"stock": {"increment": item["quantity"]}},
            )

        cancelled_order = await transaction.order.find_unique(where={"id": order_id}, include=_INCLUDE_FULL)

    return cancelled_order.model_dump()
