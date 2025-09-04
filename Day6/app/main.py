# main.py


from fastapi import FastAPI

from Day6.app.configs.database import initialize_tortoise
from Day6.app.routers.likes import like_router
from Day6.app.routers.movies import movie_router
from Day6.app.routers.reviews import review_router
from Day6.app.routers.users import user_router

app = FastAPI()

# include routers in app
app.include_router(user_router)
app.include_router(movie_router)
app.include_router(review_router)
app.include_router(like_router)

initialize_tortoise(app=app)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
