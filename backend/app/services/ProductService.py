from typing import Any

from app.repositories import ProductRepository as productRepository
from app.types.productType import (
    ProductCreateRequest,
    ProductSearchQuery,
    ProductUpdateRequest,
)
from fastapi import HTTPException, status


async def listProducts(query: ProductSearchQuery) -> dict[str, Any]:
    """
    [상품 목록 조회 서비스]
    - 검색/필터/정렬 조건에 맞는 상품과 페이지네이션 메타데이터를 함께 구성합니다.
    """
    items, totalCount = await productRepository.findMany(
        keyword=query.keyword,
        minPrice=query.minPrice,
        maxPrice=query.maxPrice,
        isAvailableOnly=query.isAvailableOnly,
        sortBy=query.sortBy,
        page=query.page,
        limit=query.limit,
    )

    totalPages = (totalCount + query.limit - 1) // query.limit if totalCount else 0

    return {
        "items": items,
        "meta": {
            "totalCount": totalCount,
            "totalPages": totalPages,
            "currentPage": query.page,
            "limit": query.limit,
            "hasNextPage": query.page < totalPages,
            "hasPrevPage": query.page > 1,
        },
    }


async def getProduct(product_id: int) -> dict[str, Any]:
    """
    [상품 상세 조회 서비스]
    """
    product = await productRepository.findById(product_id)
    if not product or product.get("deletedAt") is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 상품입니다.",
        )
    return product


async def createProduct(data: ProductCreateRequest) -> dict[str, Any]:
    """
    [상품 신규 등록 서비스] (관리자 전용)
    """
    return await productRepository.create(data.model_dump())


async def updateProduct(product_id: int, data: ProductUpdateRequest) -> dict[str, Any]:
    """
    [상품 정보 수정 서비스] (관리자 전용)
    - 수정 대상 상품이 존재하는지(소프트 딜리트되지 않았는지) 먼저 확인합니다.
    """
    await getProduct(product_id)
    return await productRepository.update(product_id, data.model_dump())


async def deleteProduct(product_id: int) -> None:
    """
    [상품 삭제(소프트 딜리트) 서비스] (관리자 전용)
    """
    await getProduct(product_id)
    await productRepository.softDelete(product_id)
