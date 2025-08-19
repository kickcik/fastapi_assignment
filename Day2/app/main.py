# main.py

from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

from Day2.app.models.movies import MovieModel
from Day2.app.router.movies import movie_router
from Day2.app.router.users import user_router
from Day2.app.schemas.movies import MovieResponse, CreateMovieRequest, MovieSearchParams, MovieUpdateParams
from Day2.app.models.users import UserModel

app = FastAPI()

# include router in app
app.include_router(user_router)
app.include_router(movie_router)

UserModel.create_dummy()  # API 테스트를 위한 더미를 생성하는 메서드 입니다.
MovieModel.create_dummy()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
