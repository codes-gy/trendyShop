from typing import Any

from app.repositories import CartRepository as cartRepository
from app.repositories import OrderRepository as orderRepository
from app.repositories import ProductRepository as productRepository
from app.types.orderType import OrderCreateRequest, PaymentApproveRequest
from fastapi import HTTPException, status


async def listOrders(user_id: int) -> list[dict[str, Any]]:
    """
    [내 주문 목록 조회 서비스]
    """
    return await orderRepository.findManyByUser(user_id)


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
    return order


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

    return await orderRepository.createOrderWithItems(
        user_id=user_id,
        address=data.address,
        total_price=total_price,
        order_items=order_items,
        cart_item_ids=data.cartItemIds,
    )


async def approvePayment(user_id: int, data: PaymentApproveRequest) -> dict[str, Any]:
    """
    [결제 승인 서비스]
    - 외부 PG사 결제창 인증이 끝난 뒤, 주문 상태와 결제 금액이 일치하는지 확인하고
      결제 정보를 생성한 뒤 주문 상태를 PAID로 전환합니다.
    """
    order = await _getOwnedOrder(data.orderId, user_id)

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

    await orderRepository.createPayment(order["id"], data.paymentKey, data.method, data.amount)
    return await orderRepository.updateStatus(order["id"], "PAID")


_CANCELLABLE_STATUSES = {"PENDING", "PAID"}


async def cancelOrder(user_id: int, order_id: int, is_admin: bool = False) -> dict[str, Any]:
    """
    [주문 취소 서비스] (주문자 본인 또는 관리자)
    - 아직 배송이 시작되지 않은(PENDING/PAID) 주문만 취소할 수 있습니다.
    - 주문 생성 시 차감했던 재고를 취소 시점에 복구합니다.
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

    order_items = [{"productId": item["productId"], "quantity": item["quantity"]} for item in order["orderItems"]]
    return await orderRepository.cancelOrderWithRestock(order_id, order_items)
