import os

import httpx
from dotenv import load_dotenv
from starlette import status
from tortoise.contrib.test import TestCase, finalizer, initializer

from Day6.app.configs import config
from Day6.app.main import app
from Day6.app.models.movies import Movie
from Day6.app.tests.utils.fake_file import fake_image

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_TEST_DB")  # 테스트 전용 DB 권장

# f-string으로 DB URL 구성
DB_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"


class TestUserRouter(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        initializer(
            ["Day6.app.models.movies"],  # 모델이 정의된 모듈 경로
            db_url=DB_URL,  # 메모리 DB 사용
        )
        super().setUpClass()
        print(DB_URL)

    @classmethod
    def tearDownClass(cls) -> None:
        finalizer()
        super().tearDownClass()

    async def test_api_create_movie(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/movies",
                json={
                    "title": "test_title",
                    "plot": "test_plot",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 90,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]
            movie = await Movie.get(id=movie_id)

        # then
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        response_json = create_response.json()

        self.assertEqual(response_json["id"], movie.id)
        self.assertEqual(response_json["title"], movie.title)
        self.assertEqual(response_json["plot"], movie.plot)
        self.assertEqual(response_json["cast"], movie.cast)
        self.assertEqual(response_json["playtime"], movie.playtime)
        self.assertEqual(response_json["genre"], movie.genre)

    async def test_api_search_movie(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/movies",
                json={
                    "title": "test_title",
                    "plot": "test_plot",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 90,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]
            movie = await Movie.get(id=movie_id)

            search_response = await client.get(
                url="/movies",
                params={"genre": "SF"},
            )
        self.assertEqual(status.HTTP_200_OK, search_response.status_code)
        response_json = search_response.json()
        self.assertEqual(response_json[0]["id"], movie.id)
        self.assertEqual(response_json[0]["title"], movie.title)
        self.assertEqual(response_json[0]["plot"], movie.plot)
        self.assertEqual(response_json[0]["cast"], movie.cast)
        self.assertEqual(response_json[0]["playtime"], movie.playtime)
        self.assertEqual(response_json[0]["genre"], movie.genre)

    async def test_api_get_movie_by_movie_id(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/movies",
                json={
                    "title": "test_title",
                    "plot": "test_plot",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 90,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]
            movie = await Movie.get(id=movie_id)

            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                create_response = await client.get(url=f"/movies/{movie_id}")

        self.assertEqual(status.HTTP_200_OK, create_response.status_code)
        response_json = create_response.json()
        self.assertEqual(response_json["id"], movie.id)
        self.assertEqual(response_json["title"], movie.title)
        self.assertEqual(response_json["plot"], movie.plot)
        self.assertEqual(response_json["cast"], movie.cast)
        self.assertEqual(response_json["playtime"], movie.playtime)
        self.assertEqual(response_json["genre"], movie.genre)

    async def test_api_patch_movie(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/movies",
                json={
                    "title": "test_title",
                    "plot": "test_plot",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 90,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                patch_response = await client.patch(
                    url=f"/movies/{movie_id}",
                    json={
                        "title": (title := "updated_title"),
                        "genre": (genre := "Adventure"),
                        "plot": (plot := "updated_plot"),
                        "cast": (
                            cast := [
                                {"name": "kim", "age": 30, "agency": "A actors", "gender": "male"},
                                {"name": "park", "age": 34, "agency": "B actors", "gender": "female"},
                            ]
                        ),
                        "playtime": (playtime := 120),
                    },
                )

        self.assertEqual(status.HTTP_200_OK, patch_response.status_code)
        response_json = patch_response.json()

        self.assertEqual(response_json["id"], movie_id)
        self.assertEqual(response_json["title"], title)
        self.assertEqual(response_json["plot"], plot)
        self.assertEqual(response_json["cast"], cast)
        self.assertEqual(response_json["genre"], genre)
        self.assertEqual(response_json["playtime"], playtime)

    async def test_api_delete_movie(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/movies",
                json={
                    "title": "test_title",
                    "plot": "test_plot",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 90,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                delete_response = await client.delete(
                    url=f"/movies/{movie_id}",
                )

        self.assertEqual(status.HTTP_204_NO_CONTENT, delete_response.status_code)

    async def test_api_register_poster_image(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/movies",
                json={
                    "title": "test_title",
                    "plot": "test_plot",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 90,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]
            movie = await Movie.get(id=movie_id)

            # when
            response = await client.post(
                f"/movies/{movie_id}/poster_image",
                files={"image": ((image := "test_image.png"), fake_image(), "image/png")},
            )

        # then
        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()

        assert f"movies/poster_images/{image.rsplit(".")[0]}" in response_json["poster_image_url"]
        assert image.rsplit(".")[1] in response_json["poster_image_url"]

        await movie.refresh_from_db()
        assert response_json["poster_image_url"] == movie.poster_image_url

        saved_file_path = os.path.join(config.MEDIA_DIR, movie.poster_image_url)
        # 파일이 저장되었는지 확인
        assert os.path.exists(saved_file_path)

        # 리소스 정리
        os.remove(saved_file_path)

    async def test_api_register_movie_poster_image_when_movie_has_profile_image_url(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                "/movies",
                json={
                    "title": "test",
                    "plot": "test 중 입니다.",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 240,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            await client.post(
                f"/movies/{movie_id}/poster_image",
                files={"image": ("test_image.png", fake_image(), "image/png")},
            )

            movie = await Movie.get(id=movie_id)
            prev_image_url = movie.poster_image_url

            # 첫번째 파일이 저장되었는지 확인
            first_file_path = os.path.join(config.MEDIA_DIR, prev_image_url)
            assert os.path.exists(first_file_path)

            # when
            response = await client.post(
                f"/movies/{movie_id}/poster_image",
                files={"image": ((second_image := "test_image2.png"), fake_image(), "image/png")},
            )
        # then
        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()

        # 파일경로와 확장자가 응답으로 반환된 poster_image_url에 포함되어 있는지 확인
        assert f"movies/poster_images/{second_image.rsplit(".")[0]}" in response_json["poster_image_url"]
        assert second_image.rsplit(".")[1] in response_json["poster_image_url"]

        await movie.refresh_from_db()
        # 응답과 Movie객체에 저장된 profile_image_url이 같은지 확인
        assert response_json["poster_image_url"] == movie.poster_image_url

        # 두번째로 등록한 파일이 저장되었는지 확인
        second_file_path = os.path.join(config.MEDIA_DIR, movie.poster_image_url)
        assert os.path.exists(second_file_path)

        # 첫번째로 등록한 파일이 삭제가 되었는지 확인
        assert not os.path.exists(first_file_path)

        # 리소스 정리
        os.remove(second_file_path)
