from typing import Annotated

from app.controllers import ReviewController as review_controller
from app.lib.passport.index import jwt_authenticate
from app.types.reviewType import (
    ReviewCreateRequest,
    ReviewListQuery,
    ReviewUpdateRequest,
)
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Review"])

_ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}


@router.get("")
async def listReviews(query: Annotated[ReviewListQuery, Depends()]):
    return await review_controller.listReviews(query)


@router.post("", status_code=status.HTTP_201_CREATED)
async def createReview(
    body: ReviewCreateRequest,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await review_controller.createReview(user.get("id"), body)


@router.patch("/{review_id}")
async def updateReview(
    review_id: int,
    body: ReviewUpdateRequest,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    return await review_controller.updateReview(user.get("id"), review_id, body)


@router.delete("/{review_id}")
async def deleteReview(
    review_id: int,
    user: Annotated[dict, Depends(jwt_authenticate)],
):
    is_admin = user.get("role") in _ADMIN_ROLES
    return await review_controller.deleteReview(user.get("id"), review_id, is_admin)
