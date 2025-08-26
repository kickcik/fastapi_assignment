from typing import Annotated, Any, Dict

from pydantic import BaseModel, Field

from Day5.app.models.movies import GenreEnum


class CreateMovieRequest(BaseModel):
    title: str
    plot: str
    cast: list[str]
    playtime: int
    genre: GenreEnum


class MovieResponse(BaseModel):
    id: int
    title: str
    plot: str
    cast: Dict[str, Any]
    playtime: int
    genre: GenreEnum

    model_config = {"from_attributes": True}  # from_orm 대신


class MovieSearchParams(BaseModel):
    title: str | None = None
    genre: GenreEnum | None = None
    plot: str | None = None
    cast: dict[str, Any] | None = None


class MovieUpdateParams(BaseModel):
    title: str | None = None
    genre: GenreEnum | None = None
    plot: str | None = None
    cast: dict[str, Any] | None = None
    playtime: Annotated[int, Field(gt=0)] | None = None
