# main.py


from fastapi import FastAPI

from Day4.app.models.movies import MovieModel
from Day4.app.models.users import UserModel
from Day4.app.routers.movies import movie_router
from Day4.app.routers.users import user_router

app = FastAPI()

# include routers in app
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
