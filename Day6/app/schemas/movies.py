from typing import Annotated, Any, Dict, List

from pydantic import BaseModel, Field

from Day6.app.models.movies import GenreEnum


class CreateMovieRequest(BaseModel):
    title: str
    plot: str
    cast: List[Dict[str, Any]]
    playtime: int
    genre: GenreEnum


class MovieResponse(BaseModel):
    id: int
    title: str
    plot: str
    cast: List[Dict[str, Any]]
    playtime: int
    genre: GenreEnum
    poster_image_url: str | None = None

    model_config = {"from_attributes": True}  # from_orm 대신


class MovieSearchParams(BaseModel):
    title: str | None = None
    genre: GenreEnum | None = None
    plot: str | None = None
    cast: List[Dict[str, Any]] | None = None


class MovieUpdateParams(BaseModel):
    title: str | None = None
    genre: GenreEnum | None = None
    plot: str | None = None
    cast: List[Dict[str, Any]] | None = None
    playtime: Annotated[int, Field(gt=0)] | None = None
