from app.services import ReviewService as reviewService
from app.types.reviewType import (
    ReviewCreateRequest,
    ReviewListQuery,
    ReviewUpdateRequest,
)


async def listReviews(query: ReviewListQuery):
    # 상품별 리뷰 목록 조회

    data = await reviewService.listReviews(query.productId, query.page, query.limit)
    return {
        "success": True,
        "message": "리뷰 목록 조회에 성공했습니다.",
        "data": data,
    }


async def createReview(user_id: int, body: ReviewCreateRequest):
    # 리뷰 작성

    data = await reviewService.createReview(user_id, body)
    return {
        "success": True,
        "message": "리뷰가 등록되었습니다.",
        "data": data,
    }


async def updateReview(user_id: int, review_id: int, body: ReviewUpdateRequest):
    # 리뷰 수정

    data = await reviewService.updateReview(user_id, review_id, body)
    return {
        "success": True,
        "message": "리뷰가 수정되었습니다.",
        "data": data,
    }


async def deleteReview(user_id: int, review_id: int, is_admin: bool):
    # 리뷰 삭제

    await reviewService.deleteReview(user_id, review_id, is_admin)
    return {
        "success": True,
        "message": "리뷰가 삭제되었습니다.",
    }
