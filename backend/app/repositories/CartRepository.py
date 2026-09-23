from typing import Any

from app.lib.prisma import db as prisma

_INCLUDE_PRODUCT = {"product": {"include": {"images": True}}}


async def findManyByUser(user_id: int) -> list[dict[str, Any]]:
    """
    [유저의 장바구니 전체 목록 조회] (상품 상세 포함)
    """
    items = await prisma.cartitem.find_many(
        where={"userId": user_id},
        include=_INCLUDE_PRODUCT,
        order={"createdAt": "desc"},
    )
    return [item.model_dump() for item in items]


async def findById(cart_item_id: int) -> dict[str, Any] | None:
    """
    [장바구니 아이템 단건 조회] (소유자 검증은 서비스 레이어에서 처리)
    """
    item = await prisma.cartitem.find_unique(
        where={"id": cart_item_id},
        include=_INCLUDE_PRODUCT,
    )
    return item.model_dump() if item else None


async def findByUserAndProduct(user_id: int, product_id: int) -> dict[str, Any] | None:
    """
    [유저-상품 조합으로 기존 장바구니 아이템 조회] (담기 시 중복 방지용)
    """
    item = await prisma.cartitem.find_unique(
        where={"userId_productId": {"userId": user_id, "productId": product_id}},
    )
    return item.model_dump() if item else None


async def create(user_id: int, product_id: int, quantity: int) -> dict[str, Any]:
    """
    [장바구니 아이템 신규 생성]
    """
    new_item = await prisma.cartitem.create(
        data={"userId": user_id, "productId": product_id, "quantity": quantity},
        include=_INCLUDE_PRODUCT,
    )
    return new_item.model_dump()


async def updateQuantity(cart_item_id: int, quantity: int) -> dict[str, Any]:
    """
    [장바구니 아이템 수량 변경]
    """
    updated_item = await prisma.cartitem.update(
        where={"id": cart_item_id},
        data={"quantity": quantity},
        include=_INCLUDE_PRODUCT,
    )
    return updated_item.model_dump()


async def delete(cart_item_id: int) -> None:
    """
    [장바구니 아이템 삭제]
    """
    await prisma.cartitem.delete(where={"id": cart_item_id})
