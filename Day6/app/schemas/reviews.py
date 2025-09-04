from __future__ import annotations

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    title: str
    content: str
    review_image_url: str | None = None


class CreateReviewRequest(BaseModel):
    movie_id: int
    title: str
    content: str
    review_image: UploadFile | None = File(None)

    @classmethod
    def as_form(
        cls,
        movie_id: int = Form(...),
        title: str = Form(...),
        content: str = Form(...),
        review_image: UploadFile | None = File(None),
    ) -> CreateReviewRequest:
        return cls(movie_id=movie_id, title=title, content=content, review_image=review_image)


class UpdateReviewRequest(BaseModel):
    title: str
    content: str
    review_image: UploadFile | None = File(None)

    @classmethod
    def as_form(
        cls, title: str = Form(...), content: str = Form(...), review_image: UploadFile | None = Form()
    ) -> UpdateReviewRequest:
        return cls(title=title, content=content, review_image=review_image)
