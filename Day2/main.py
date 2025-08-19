# main.py

from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

from Day2.app.models.movies import MovieModel
from Day2.app.schemas.movies import MovieResponse, CreateMovieRequest, MovieSearchParams, MovieUpdateParams
from app.models.users import UserModel

app = FastAPI()

UserModel.create_dummy()  # API 테스트를 위한 더미를 생성하는 메서드 입니다.
MovieModel.create_dummy()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.post("/movies", response_model=MovieResponse, status_code=201)  # 영화 등록
def create_movie(movie: CreateMovieRequest) -> MovieResponse:
    new_movie = MovieModel(**movie.model_dump())
    return MovieResponse.model_validate(new_movie)


@app.get("/movies", response_model=list[MovieResponse], status_code=200)  # 영화 검색
async def search_movie(query_params: Annotated[MovieSearchParams, Query()]) -> list[MovieResponse]:
    valid_query = {key: value for key, value in query_params.model_dump().items() if value is not None}

    if filtered_movie_list := MovieModel.filter(**valid_query):
        return [MovieResponse.model_validate(movie) for movie in filtered_movie_list]
    else:
        return [MovieResponse.model_validate(movie) for movie in MovieModel.all()]


@app.get("/movies/{movie_id}", response_model=MovieResponse, status_code=200)  # 특정 영화 검색
def read_movie(movie_id: int = Path(gt=0)) -> MovieResponse:
    if movie := MovieModel.get(id=movie_id):
        return MovieResponse.model_validate(movie)
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@app.patch("/movie/{movie_id}", response_model=MovieResponse, status_code=200)  # 영화 갱신
def update_movie(data: MovieUpdateParams, movie_id: int = Path(gt=0)) -> MovieResponse:
    if movie := MovieModel.get(id=movie_id):
        movie.upate(**data.model_dump())
        return MovieResponse.model_validate(movie)
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@app.delete("/movie/{movie_id}", status_code=204)
async def delete_movie(movie_id: int = Path(gt=0)) -> None:
    if movie := MovieModel.get(id=movie_id):
        movie.delete()
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
