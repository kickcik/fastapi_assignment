from typing import Annotated

from fastapi import APIRouter, Depends

from Day6.app.models.likes import ReviewLike
from Day6.app.models.users import User
from Day6.app.schemas.likes import ReviewLikeResponse
from Day6.app.utils.auth import get_current_user

like_router = APIRouter(prefix="/likes", tags=["likes"])


@like_router.get("/reviews/{review_id}/like", status_code=200)
async def like_review(user: Annotated[User, Depends(get_current_user)], review_id: int) -> None:
    review_like, _ = await ReviewLike.get_or_create(user_id=user.id, review_id=review_id)

    if not review_like.is_liked:
        review_like.is_liked = True
        await review_like.save()


@like_router.get("/reviews/{review_id}/unlike", status_code=200)
async def unlike_review(user: Annotated[User, Depends(get_current_user)], review_id: int) -> ReviewLikeResponse:
    if not (review_like := await ReviewLike.get_or_none(user_id=user.id, review_id=review_id)):
        return ReviewLikeResponse(user_id=user.id, review_id=review_id, is_liked=False)

    if review_like.is_liked:
        review_like.is_liked = False
        await review_like.save()

    return ReviewLikeResponse(
        id=review_like.id,
        user_id=review_like.user_id,  # type: ignore[attr-defined]
        review_id=review_like.review_id,  # type: ignore[attr-defined]
        is_liked=review_like.is_liked,
    )
