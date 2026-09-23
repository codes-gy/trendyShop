from typing import Any

from app.repositories import OrderRepository as orderRepository
from app.repositories import ReviewRepository as reviewRepository
from app.services import ProductService as productService
from app.types.reviewType import ReviewCreateRequest, ReviewUpdateRequest
from fastapi import HTTPException, status
from prisma.errors import UniqueViolationError


async def listReviews(product_id: int, page: int, limit: int) -> dict[str, Any]:
    """
    [상품별 리뷰 목록 조회 서비스]
    """
    await productService.getProduct(product_id)  # 존재하지 않는 상품이면 404

    items, totalCount = await reviewRepository.findManyByProduct(product_id, page, limit)
    totalPages = (totalCount + limit - 1) // limit if totalCount else 0

    return {
        "items": items,
        "meta": {
            "totalCount": totalCount,
            "totalPages": totalPages,
            "currentPage": page,
            "limit": limit,
            "hasNextPage": page < totalPages,
            "hasPrevPage": page > 1,
        },
    }


async def createReview(user_id: int, data: ReviewCreateRequest) -> dict[str, Any]:
    """
    [리뷰 작성 서비스]
    - 실제로 구매(결제 완료 이상)한 상품에 대해서만 리뷰를 작성할 수 있습니다.
    - 같은 상품에 대해 한 번만 리뷰를 작성할 수 있습니다.
    """
    await productService.getProduct(data.productId)  # 존재하지 않는 상품이면 404

    purchased = await orderRepository.hasPurchasedProduct(user_id, data.productId)
    if not purchased:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="구매한 상품에 대해서만 리뷰를 작성할 수 있습니다.",
        )

    existing = await reviewRepository.findByUserAndProduct(user_id, data.productId)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 리뷰를 작성한 상품입니다.",
        )

    try:
        return await reviewRepository.create(user_id, data.productId, data.rating, data.comment)
    except UniqueViolationError:
        # 동시 요청 경합(race condition)으로 애플리케이션 레벨 중복 체크를 통과했더라도,
        # DB의 (userId, productId) 유니크 제약이 최종 방어선 역할을 합니다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 리뷰를 작성한 상품입니다.",
        ) from None


async def _getOwnedReview(review_id: int, user_id: int) -> dict[str, Any]:
    review = await reviewRepository.findById(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 리뷰입니다.",
        )
    if review["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인이 작성한 리뷰만 수정/삭제할 수 있습니다.",
        )
    return review


async def updateReview(user_id: int, review_id: int, data: ReviewUpdateRequest) -> dict[str, Any]:
    """
    [리뷰 수정 서비스] (작성자 본인만 가능)
    """
    await _getOwnedReview(review_id, user_id)
    return await reviewRepository.update(review_id, data.model_dump())


async def deleteReview(user_id: int, review_id: int, is_admin: bool = False) -> None:
    """
    [리뷰 삭제 서비스] (작성자 본인 또는 관리자)
    """
    review = await reviewRepository.findById(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 리뷰입니다.",
        )
    if not is_admin and review["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인이 작성한 리뷰만 삭제할 수 있습니다.",
        )

    await reviewRepository.delete(review_id)
