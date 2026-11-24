import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.lib import payment as paymentGateway
from app.lib.env import ORDER_PENDING_EXPIRATION_MINUTES
from app.repositories import CartRepository as cartRepository
from app.repositories import OrderRepository as orderRepository
from app.repositories import ProductRepository as productRepository
from app.repositories.OrderRepository import InsufficientStockError, OrderStatusConflictError
from app.types.orderType import OrderCreateRequest, PaymentApproveRequest
from fastapi import HTTPException, status
from prisma.errors import UniqueViolationError

logger = logging.getLogger(__name__)


async def listOrders(user_id: int) -> list[dict[str, Any]]:
    """
    [내 주문 목록 조회 서비스]
    """
    return await orderRepository.findManyByUser(user_id)


async def _expireIfStale(order: dict[str, Any]) -> dict[str, Any]:
    """
    [결제 대기 주문 자동 만료 처리]
    - PENDING 상태로 ORDER_PENDING_EXPIRATION_MINUTES 이상 방치된 주문을
      조회/결제 승인 시점에 지연 평가(lazy evaluation)로 자동 취소하고 재고를 복구합니다.
    - 별도의 백그라운드 스케줄러 없이 동작하는 간단한 방식이라, 아무도 접근하지 않는
      주문은 만료 시각이 지나도 즉시 정리되지는 않는다는 한계가 있습니다.
      (대량의 방치 주문을 주기적으로 정리하려면 스케줄러 기반 배치가 더 적합합니다.)
    """
    if order["status"] != "PENDING":
        return order

    elapsed = datetime.now(UTC) - order["createdAt"]
    if elapsed < timedelta(minutes=ORDER_PENDING_EXPIRATION_MINUTES):
        return order

    order_items = [{"productId": item["productId"], "quantity": item["quantity"]} for item in order["orderItems"]]
    try:
        return await orderRepository.cancelOrderWithRestock(order["id"], order_items, from_statuses=["PENDING"])
    except OrderStatusConflictError:
        # 그 사이 다른 요청이 먼저 결제/취소 처리한 경우: 재고는 건드리지 않고 최신 상태를 다시 읽어 반환합니다.
        return await orderRepository.findById(order["id"])


async def _getOwnedOrder(order_id: int, user_id: int) -> dict[str, Any]:
    order = await orderRepository.findById(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 주문입니다.",
        )
    if order["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 주문만 조회할 수 있습니다.",
        )
    return await _expireIfStale(order)


async def getOrder(order_id: int, user_id: int) -> dict[str, Any]:
    """
    [주문 상세 조회 서비스]
    """
    return await _getOwnedOrder(order_id, user_id)


async def createOrder(user_id: int, data: OrderCreateRequest) -> dict[str, Any]:
    """
    [주문 생성 서비스 (체크아웃)]
    - 선택한 장바구니 아이템들이 전부 본인 소유인지, 상품이 판매 가능하고
      재고가 충분한지 검증한 뒤 주문 스냅샷을 만들고 재고를 차감합니다.
    - 여기서의 재고 확인은 빠른 실패(fail-fast)용이며, 실제 재고 보장은 주문 트랜잭션 안의
      조건부 차감(stock >= 수량일 때만 차감)이 담당합니다. 확인 시점과 차감 시점 사이에
      다른 주문이 재고를 가져가면 409로 거절되고 트랜잭션 전체가 롤백됩니다.
    """
    cart_items = []
    for cart_item_id in data.cartItemIds:
        cart_item = await cartRepository.findById(cart_item_id)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"존재하지 않는 장바구니 아이템입니다. (id={cart_item_id})",
            )
        if cart_item["userId"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="본인의 장바구니 아이템만 주문할 수 있습니다.",
            )
        cart_items.append(cart_item)

    order_items = []
    total_price = 0
    for cart_item in cart_items:
        product = await productRepository.findById(cart_item["productId"])
        if not product or product.get("deletedAt") is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"존재하지 않는 상품이 포함되어 있습니다. (productId={cart_item['productId']})",
            )
        if not product["isAvailable"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"판매 중지된 상품이 포함되어 있습니다. ({product['name']})",
            )
        if cart_item["quantity"] > product["stock"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"재고가 부족한 상품이 있습니다. ({product['name']})",
            )

        item_total_price = product["price"] * cart_item["quantity"]
        total_price += item_total_price
        order_items.append(
            {
                "productId": product["id"],
                "price": product["price"],
                "quantity": cart_item["quantity"],
                "totalPrice": item_total_price,
            }
        )

    try:
        return await orderRepository.createOrderWithItems(
            user_id=user_id,
            address=data.address,
            total_price=total_price,
            order_items=order_items,
            cart_item_ids=data.cartItemIds,
        )
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"재고가 부족하거나 판매 중지된 상품이 있습니다. (productId={e.product_id})",
        ) from None


# 토스페이먼츠 승인 응답의 method(한글) → 우리 PaymentMethod enum
_PG_METHOD_MAP = {
    "카드": "CARD",
    "간편결제": "CARD",
    "계좌이체": "TRANSFER",
    "가상계좌": "VIRTUAL_ACCOUNT",
}


async def approvePayment(user_id: int, data: PaymentApproveRequest) -> dict[str, Any]:
    """
    [결제 승인 서비스]
    1. 주문 소유자/상태(PENDING)/금액(서버에 저장된 주문 금액 기준)을 검증합니다.
    2. PG사 결제 승인 API를 서버에서 직접 호출해, 실제로 승인된 금액/주문번호/paymentKey를 다시 확인합니다.
       (클라이언트가 보낸 paymentKey/amount만으로는 결제 완료 처리하지 않습니다.)
    3. 결제 정보 저장 + 주문 PAID 전환을 하나의 트랜잭션(PENDING인 경우에만 전환)으로 처리합니다.
       paymentKey는 DB 유니크 제약으로 한 번만 사용할 수 있습니다.
    """
    order = await _getOwnedOrder(data.orderId, user_id)

    if order["status"] == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 취소된 주문입니다. (결제 대기 시간이 만료되었을 수 있습니다.)",
        )

    if order["status"] != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="결제 대기 상태의 주문이 아닙니다.",
        )

    if data.amount != order["totalPrice"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="결제 금액이 주문 금액과 일치하지 않습니다.",
        )

    pg_order_id = paymentGateway.toPgOrderId(order["id"])
    try:
        # 승인 요청 금액도 클라이언트 값이 아니라 서버에 저장된 주문 금액을 사용합니다.
        confirmation = await paymentGateway.getPaymentGateway().confirm(
            data.paymentKey, pg_order_id, order["totalPrice"]
        )
    except paymentGateway.PaymentGatewayError as e:
        logger.warning("결제 승인 실패 orderId=%s code=%s message=%s", order["id"], e.code, e.message)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY if e.retryable else status.HTTP_400_BAD_REQUEST,
            detail=f"결제 승인에 실패했습니다. ({e.message})",
        ) from None

    if (
        confirmation.status != "DONE"
        or confirmation.total_amount != order["totalPrice"]
        or confirmation.pg_order_id != pg_order_id
        or confirmation.payment_key != data.paymentKey
    ):
        # PG 승인 결과가 주문과 맞지 않으면 결제 완료로 처리하지 않습니다. (PG 측 자동 취소는 아직 미구현)
        logger.error(
            "PG 승인 결과 불일치 orderId=%s expected=(%s, %s) actual=(%s, %s, %s)",
            order["id"],
            pg_order_id,
            order["totalPrice"],
            confirmation.pg_order_id,
            confirmation.total_amount,
            confirmation.status,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="결제 승인 결과가 주문 정보와 일치하지 않습니다.",
        )

    method = _PG_METHOD_MAP.get(confirmation.method or "", data.method)
    try:
        return await orderRepository.markPaidWithPayment(
            order["id"], data.paymentKey, method, confirmation.total_amount
        )
    except (OrderStatusConflictError, UniqueViolationError):
        # PG 승인은 끝났지만 그 사이 주문이 만료/취소되었거나 이미 결제가 저장된 경우.
        # 실제로 돈이 빠져나간 상태일 수 있으므로 운영자가 확인(환불)할 수 있게 에러 로그를 남깁니다.
        logger.error(
            "PG 승인 후 주문 결제 처리 실패 - 수동 확인/환불 필요 orderId=%s paymentKey=%s",
            order["id"],
            data.paymentKey,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 결제되었거나 취소된 주문입니다.",
        ) from None


_CANCELLABLE_STATUSES = ["PENDING", "PAID"]


async def cancelOrder(user_id: int, order_id: int, is_admin: bool = False) -> dict[str, Any]:
    """
    [주문 취소 서비스] (주문자 본인 또는 관리자)
    - 아직 배송이 시작되지 않은(PENDING/PAID) 주문만 취소할 수 있습니다.
    - 결제 완료(PAID) 주문은 PG 환불 연동 전까지 관리자만 취소할 수 있습니다. (관리자 취소 시 수동 환불 필요)
    - 주문 생성 시 차감했던 재고를 취소 시점에 복구합니다. (상태 전환에 성공한 경우에만 한 번)
    """
    order = await orderRepository.findById(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 주문입니다.",
        )
    if not is_admin and order["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 주문만 취소할 수 있습니다.",
        )
    if order["status"] not in _CANCELLABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="배송이 시작되었거나 이미 완료/취소된 주문은 취소할 수 없습니다.",
        )
    if order["status"] == "PAID" and not is_admin:
        # PG 환불(결제 취소) 연동이 아직 없어서, 사용자가 결제 완료 주문을 직접 취소하면 재고만 복구되고
        # 결제 금액은 돌려받지 못합니다. 환불이 자동화될 때까지는 관리자를 통해서만 취소하도록 막습니다.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="결제 완료된 주문은 환불 처리가 필요하여 고객센터(관리자)를 통해서만 취소할 수 있습니다.",
        )

    order_items = [{"productId": item["productId"], "quantity": item["quantity"]} for item in order["orderItems"]]
    try:
        # 조회 시점에 확인한 상태 그대로일 때만 취소합니다. (예: 사용자가 PENDING 주문을 취소하는 사이
        # 결제가 승인되어 PAID가 되었다면, 환불 없이 PAID 주문이 취소되지 않도록 409로 거절됩니다.)
        cancelled = await orderRepository.cancelOrderWithRestock(order_id, order_items, from_statuses=[order["status"]])
    except OrderStatusConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="주문 상태가 이미 변경되어 취소할 수 없습니다. (이미 취소되었거나 배송이 시작되었을 수 있습니다.)",
        ) from None

    if order["status"] == "PAID":
        # 관리자가 결제 완료 주문을 취소한 경우: PG 환불은 자동으로 이루어지지 않으므로 수동 환불이 필요합니다.
        logger.warning(
            "결제 완료 주문 취소 - PG 수동 환불 필요 orderId=%s paymentKey=%s",
            order_id,
            (order.get("payment") or {}).get("paymentKey"),
        )
    return cancelled
