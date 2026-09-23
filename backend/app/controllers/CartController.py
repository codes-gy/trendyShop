from app.services import CartService as cartService
from app.types.cartType import CartItemCreateRequest, CartItemUpdateRequest


async def listCart(user_id: int):
    # 내 장바구니 목록 조회

    data = await cartService.listCart(user_id)
    return {
        "success": True,
        "message": "장바구니 조회에 성공했습니다.",
        "data": data,
    }


async def addItem(user_id: int, body: CartItemCreateRequest):
    # 장바구니에 상품 담기

    data = await cartService.addItem(user_id, body)
    return {
        "success": True,
        "message": "장바구니에 상품을 담았습니다.",
        "data": data,
    }


async def updateItem(user_id: int, cart_item_id: int, body: CartItemUpdateRequest):
    # 장바구니 아이템 수량 변경

    data = await cartService.updateItem(user_id, cart_item_id, body)
    return {
        "success": True,
        "message": "장바구니 수량이 변경되었습니다.",
        "data": data,
    }


async def removeItem(user_id: int, cart_item_id: int):
    # 장바구니 아이템 삭제

    await cartService.removeItem(user_id, cart_item_id)
    return {
        "success": True,
        "message": "장바구니에서 상품을 삭제했습니다.",
    }
