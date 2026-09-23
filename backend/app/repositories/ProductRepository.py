from datetime import UTC, datetime
from typing import Any

from app.lib.prisma import db as prisma


def _buildWhere(
    keyword: str | None,
    minPrice: int | None,
    maxPrice: int | None,
    isAvailableOnly: bool,
) -> dict[str, Any]:
    """[목록 조회용 where 절 빌더]
    - 소프트 딜리트(deletedAt이 채워진) 상품은 항상 목록/검색에서 제외합니다.
    """
    where: dict[str, Any] = {"deletedAt": None}

    if keyword:
        where["name"] = {"contains": keyword, "mode": "insensitive"}

    priceFilter: dict[str, Any] = {}
    if minPrice is not None:
        priceFilter["gte"] = minPrice
    if maxPrice is not None:
        priceFilter["lte"] = maxPrice
    if priceFilter:
        where["price"] = priceFilter

    if isAvailableOnly:
        where["isAvailable"] = True

    return where


def _buildOrderBy(sortBy: str) -> list[dict[str, str]]:
    if sortBy == "priceAsc":
        return [{"price": "asc"}]
    if sortBy == "priceDesc":
        return [{"price": "desc"}]
    return [{"createdAt": "desc"}]


async def findMany(
    keyword: str | None,
    minPrice: int | None,
    maxPrice: int | None,
    isAvailableOnly: bool,
    sortBy: str,
    page: int,
    limit: int,
) -> tuple[list[dict[str, Any]], int]:
    """
    [상품 목록 조회 (검색/필터/정렬/페이지네이션)]
    - 상품 리스트와 조건에 맞는 전체 개수를 함께 반환합니다.
    """
    where = _buildWhere(keyword, minPrice, maxPrice, isAvailableOnly)
    orderBy = _buildOrderBy(sortBy)
    skip = (page - 1) * limit

    items = await prisma.product.find_many(
        where=where,
        order=orderBy,
        skip=skip,
        take=limit,
        include={"images": True},
    )
    totalCount = await prisma.product.count(where=where)

    return [item.model_dump() for item in items], totalCount


async def findById(product_id: int) -> dict[str, Any] | None:
    """
    [상품 단건 조회 (이미지 포함)]
    """
    product = await prisma.product.find_unique(
        where={"id": product_id},
        include={"images": True},
    )
    return product.model_dump() if product else None


async def create(data: dict[str, Any]) -> dict[str, Any]:
    """
    [상품 신규 등록]
    """
    new_product = await prisma.product.create(
        data={
            "name": data["name"],
            "description": data.get("description"),
            "price": data["price"],
            "stock": data["stock"],
        },
        include={"images": True},
    )
    return new_product.model_dump()


async def update(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    [상품 정보 부분 수정]
    - None이 아닌(=요청에 포함된) 필드만 갱신 데이터로 전달합니다.
    """
    update_data = {key: value for key, value in data.items() if value is not None}

    updated_product = await prisma.product.update(
        where={"id": product_id},
        data=update_data,
        include={"images": True},
    )
    return updated_product.model_dump()


async def softDelete(product_id: int) -> dict[str, Any]:
    """
    [상품 소프트 딜리트]
    - 실제로 행을 삭제하지 않고 deletedAt을 채우고 판매 불가 상태로 전환합니다.
    """
    deleted_product = await prisma.product.update(
        where={"id": product_id},
        data={"deletedAt": datetime.now(UTC), "isAvailable": False},
    )
    return deleted_product.model_dump()
