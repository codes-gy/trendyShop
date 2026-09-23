from app.services import OrderService as orderService
from app.types.orderType import OrderCreateRequest, PaymentApproveRequest


async def listOrders(user_id: int):
    # 내 주문 목록 조회

    data = await orderService.listOrders(user_id)
    return {
        "success": True,
        "message": "주문 목록 조회에 성공했습니다.",
        "data": data,
    }


async def getOrder(user_id: int, order_id: int):
    # 주문 상세 조회

    data = await orderService.getOrder(order_id, user_id)
    return {
        "success": True,
        "message": "주문 조회에 성공했습니다.",
        "data": data,
    }


async def createOrder(user_id: int, body: OrderCreateRequest):
    # 주문 생성 (체크아웃)

    data = await orderService.createOrder(user_id, body)
    return {
        "success": True,
        "message": "주문이 생성되었습니다.",
        "data": data,
    }


async def approvePayment(user_id: int, body: PaymentApproveRequest):
    # 결제 승인

    data = await orderService.approvePayment(user_id, body)
    return {
        "success": True,
        "message": "결제가 승인되었습니다.",
        "data": data,
    }


async def cancelOrder(user_id: int, order_id: int, is_admin: bool):
    # 주문 취소

    data = await orderService.cancelOrder(user_id, order_id, is_admin)
    return {
        "success": True,
        "message": "주문이 취소되었습니다.",
        "data": data,
    }
