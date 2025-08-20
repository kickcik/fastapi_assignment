from pydantic import BaseModel


class CreateMovieRequest(BaseModel):
    title: str
    playtime: int
    genre: list[str]


class MovieResponse(BaseModel):
    id: int
    title: str
    playtime: int
    genre: list[str]

    model_config = {"from_attributes": True}  # from_orm 대신


class MovieSearchParams(BaseModel):
    title: str | None = None
    genre: list[str] | None = None


class MovieUpdateParams(BaseModel):
    title: str | None = None
    playtime: int | None = None
    genre: list[str] | None = None
