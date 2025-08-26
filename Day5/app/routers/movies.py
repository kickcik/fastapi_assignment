from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, UploadFile

from Day5.app.models.movies import Movie
from Day5.app.schemas.movies import (
    CreateMovieRequest,
    MovieResponse,
    MovieSearchParams,
    MovieUpdateParams,
)
from Day5.app.utils.file import delete_file, upload_file, validate_image_extension

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

    @movie_router.post("/{movie_id}/poster_image", response_model=MovieResponse, status_code=201)
    async def register_poster_image(image: UploadFile, movie_id: int = Path(gt=0)) -> MovieResponse:
        validate_image_extension(image)

        if not (movie := await Movie.get_or_none(id=movie_id)):
            raise HTTPException(status_code=404, detail="Movie not found")

        prev_image_url = movie.poster_image_url
        try:
            image_url = await upload_file(image, "movies/poster_images")
            movie.poster_image_url = image_url
            await movie.save()

            if prev_image_url is not None:
                delete_file(prev_image_url)

            return MovieResponse.model_validate(movie)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
