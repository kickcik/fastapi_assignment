from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from Day4.app.models.movies import Movie
from Day4.app.schemas.movies import (
    CreateMovieRequest,
    MovieResponse,
    MovieSearchParams,
    MovieUpdateParams,
)

movie_router = APIRouter(prefix="/movies", tags=["movies"])


@movie_router.post("", response_model=MovieResponse, status_code=201)  # 영화 등록
async def create_movie(movie: CreateMovieRequest) -> MovieResponse:
    new_movie = await Movie.create(**movie.model_dump())
    return MovieResponse.model_validate(new_movie)


@movie_router.get("", response_model=list[MovieResponse], status_code=200)  # 영화 검색
async def search_movie(query_params: Annotated[MovieSearchParams, Query()]) -> list[Movie]:
    valid_query = {key: value for key, value in query_params.model_dump().items() if value is not None}
    return await Movie.filter(**valid_query).all()


@movie_router.get("/{movie_id}", response_model=MovieResponse, status_code=200)  # 특정 영화 검색
async def read_movie(movie_id: int = Path(gt=0)) -> MovieResponse:
    if movie := await Movie.get_or_none(id=movie_id):
        return MovieResponse.model_validate(movie)
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@movie_router.patch("/{movie_id}", response_model=MovieResponse, status_code=200)  # 영화 갱신
async def update_movie(data: MovieUpdateParams, movie_id: int = Path(gt=0)) -> MovieResponse:
    if movie := await Movie.get_or_none(id=movie_id):
        valid_params = {key: value for key, value in data.model_dump().items() if value is not None}
        await movie.update_from_dict(**valid_params)
        await movie.save()
        return MovieResponse.model_validate(movie)
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@movie_router.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: int = Path(gt=0)) -> None:
    if movie := await Movie.get(id=movie_id):
        await movie.delete()
    else:
        raise HTTPException(status_code=404, detail="Movie not found")
