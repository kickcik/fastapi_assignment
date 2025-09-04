from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from Day6.app.models.likes import ReviewLike
from Day6.app.models.reviews import Review
from Day6.app.models.users import User
from Day6.app.schemas.likes import ReviewIsLikedResponse, ReviewLikeCountResponse
from Day6.app.schemas.reviews import (
    CreateReviewRequest,
    ReviewResponse,
    UpdateReviewRequest,
)
from Day6.app.utils.auth import get_current_user
from Day6.app.utils.file import delete_file, upload_file

review_router = APIRouter(prefix="/reviews", tags=["reviews"])


@review_router.post("/", status_code=201)
async def create_review(
    user: Annotated[User, Depends(get_current_user)],
    review_form: Annotated[CreateReviewRequest, Depends(CreateReviewRequest.as_form)],
) -> ReviewResponse:
    data = {
        "user_id": user.id,
        "movie_id": review_form.movie_id,
        "title": review_form.title,
        "content": review_form.content,
    }

    if review_form.review_image:
        data["review_image_url"] = await upload_file(review_form.review_image, "reviews/images")

    review = await Review.create(**data)  # type: ignore[arg-type]

    return ReviewResponse.model_validate(review)


@review_router.get("/{review_id}", status_code=200)
async def get_review(review_id: int) -> ReviewResponse:
    if review := await Review.get_or_none(id=review_id):
        return ReviewResponse.model_validate(review)
    raise HTTPException(status_code=404, detail="Review does not exist")


@review_router.patch("/{review_id}")
async def update_review(
    user: Annotated[User, Depends(get_current_user)],
    review_id: int,
    update_form: Annotated[UpdateReviewRequest, Depends(UpdateReviewRequest.as_form)],
) -> ReviewResponse:
    if not (review := await Review.get_or_none(id=review_id)):
        raise HTTPException(status_code=404, detail="Review does not exist")

    if not (update_form.title and update_form.content):
        raise HTTPException(status_code=404, detail="Review does not exist")

    if review.user_id != user.id:  # type: ignore[attr-defined]
        raise HTTPException(status_code=403, detail="You are not the owner of the review")

    review.title = UpdateReviewRequest.title if UpdateReviewRequest.title is not None else review.title
    review.content = UpdateReviewRequest.content if UpdateReviewRequest.content is not None else review.content

    if UpdateReviewRequest.review_image:
        prev_image_url = review.review_image_url
        review.review_image_url = await upload_file(UpdateReviewRequest.review_image, "reviews/images")

        if prev_image_url is not None:
            delete_file(prev_image_url)

    await review.save()

    return ReviewResponse.model_validate(review)


@review_router.delete("/{review_id}", status_code=204)
async def delete_review(user: Annotated[User, Depends(get_current_user)], review_id: int) -> None:
    if not (review := await Review.get_or_none(id=review_id)):
        raise HTTPException(status_code=404, detail="Review does not exist")

    if review.user_id != user.id:  # type: ignore[attr-defined]
        raise HTTPException(status_code=403, detail="You are not the owner of the review")
    await review.delete()


@review_router.get("/{review_id}/like_count")
async def get_review_like_count(review_id: int) -> ReviewLikeCountResponse:
    likes = await Review.filter(id=review_id).count()
    return ReviewLikeCountResponse(review_id=review_id, like_count=likes)


@review_router.get("/{review_id}/is_liked")
async def get_review_is_liked(
    user: Annotated[User, Depends(get_current_user)], review_id: int = Path(gt=0)
) -> ReviewIsLikedResponse:
    if review_like := await ReviewLike.get_or_none(id=review_id, user_id=user.id):
        return ReviewIsLikedResponse(review_id=review_id, user_id=user.id, is_liked=review_like.is_liked)
    return ReviewIsLikedResponse(review_id=review_id, user_id=user.id, is_liked=False)
