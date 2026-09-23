from typing import Any

from app.repositories import CartRepository as cartRepository
from app.services import ProductService as productService
from app.types.cartType import CartItemCreateRequest, CartItemUpdateRequest
from fastapi import HTTPException, status


async def listCart(user_id: int) -> list[dict[str, Any]]:
    """
    [내 장바구니 목록 조회 서비스]
    """
    return await cartRepository.findManyByUser(user_id)


async def _assertOwnership(cart_item: dict[str, Any], user_id: int) -> None:
    if cart_item["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 장바구니만 접근할 수 있습니다.",
        )


async def _getOwnedCartItem(cart_item_id: int, user_id: int) -> dict[str, Any]:
    cart_item = await cartRepository.findById(cart_item_id)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 장바구니 아이템입니다.",
        )
    await _assertOwnership(cart_item, user_id)
    return cart_item


async def addItem(user_id: int, data: CartItemCreateRequest) -> dict[str, Any]:
    """
    [장바구니 아이템 추가 서비스]
    - 상품 존재/판매 여부를 확인합니다.
    - 이미 담겨있는 상품이면 수량을 더하고(merge), 없으면 새로 생성합니다.
    - 재고를 초과하는 수량은 담을 수 없습니다.
    """
    product = await productService.getProduct(data.productId)

    if not product["isAvailable"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="판매 중지된 상품은 장바구니에 담을 수 없습니다.",
        )

    existing = await cartRepository.findByUserAndProduct(user_id, data.productId)
    new_quantity = (existing["quantity"] if existing else 0) + data.quantity

    if new_quantity > product["stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="재고 수량을 초과하여 담을 수 없습니다.",
        )

    if existing:
        return await cartRepository.updateQuantity(existing["id"], new_quantity)
    return await cartRepository.create(user_id, data.productId, data.quantity)


async def updateItem(user_id: int, cart_item_id: int, data: CartItemUpdateRequest) -> dict[str, Any]:
    """
    [장바구니 아이템 수량 변경 서비스]
    """
    cart_item = await _getOwnedCartItem(cart_item_id, user_id)

    product = await productService.getProduct(cart_item["productId"])
    if data.quantity > product["stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="재고 수량을 초과하여 담을 수 없습니다.",
        )

    return await cartRepository.updateQuantity(cart_item_id, data.quantity)


async def removeItem(user_id: int, cart_item_id: int) -> None:
    """
    [장바구니 아이템 삭제 서비스]
    """
    await _getOwnedCartItem(cart_item_id, user_id)
    await cartRepository.delete(cart_item_id)
