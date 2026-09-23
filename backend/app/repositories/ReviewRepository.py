from typing import Any

from app.lib.prisma import db as prisma

_INCLUDE_USER = {"user": True}


async def findManyByProduct(product_id: int, page: int, limit: int) -> tuple[list[dict[str, Any]], int]:
    """
    [상품별 리뷰 목록 조회] (페이지네이션)
    """
    skip = (page - 1) * limit
    where = {"productId": product_id}

    items = await prisma.review.find_many(
        where=where,
        include=_INCLUDE_USER,
        order={"createdAt": "desc"},
        skip=skip,
        take=limit,
    )
    totalCount = await prisma.review.count(where=where)

    return [item.model_dump() for item in items], totalCount


async def findById(review_id: int) -> dict[str, Any] | None:
    """
    [리뷰 단건 조회]
    """
    review = await prisma.review.find_unique(
        where={"id": review_id},
        include=_INCLUDE_USER,
    )
    return review.model_dump() if review else None


async def findByUserAndProduct(user_id: int, product_id: int) -> dict[str, Any] | None:
    """
    [유저-상품 조합으로 기존 리뷰 조회] (중복 작성 방지용)
    """
    review = await prisma.review.find_first(
        where={"userId": user_id, "productId": product_id},
    )
    return review.model_dump() if review else None


async def create(user_id: int, product_id: int, rating: int, comment: str) -> dict[str, Any]:
    """
    [리뷰 신규 작성]
    """
    new_review = await prisma.review.create(
        data={
            "userId": user_id,
            "productId": product_id,
            "rating": rating,
            "comment": comment,
        },
        include=_INCLUDE_USER,
    )
    return new_review.model_dump()


async def update(review_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    [리뷰 부분 수정]
    """
    update_data = {key: value for key, value in data.items() if value is not None}

    updated_review = await prisma.review.update(
        where={"id": review_id},
        data=update_data,
        include=_INCLUDE_USER,
    )
    return updated_review.model_dump()


async def delete(review_id: int) -> None:
    """
    [리뷰 삭제]
    """
    await prisma.review.delete(where={"id": review_id})
