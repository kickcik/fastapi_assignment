import os

import httpx
from dotenv import load_dotenv
from tortoise.contrib.test import TestCase, finalizer, initializer

from Day5.app.main import app
from Day5.app.models.users import User
from Day5.app.utils.auth import verify_password

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
            ["Day5.app.models.users"],  # 모델이 정의된 모듈 경로
            db_url=DB_URL,  # 메모리 DB 사용
        )
        super().setUpClass()
        print(DB_URL)

    @classmethod
    def tearDownClass(cls) -> None:
        finalizer()
        super().tearDownClass()

    async def test_api_get_all_users(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            await client.post(
                "/users",
                json={
                    "username": "test",
                    "password": "1234",
                    "age": 20,
                    "gender": "male",
                },
            )
            response = await client.get("/users")
        self.assertEqual(response.status_code, 200)

    async def test_api_get_all_users_none(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/users")
        self.assertEqual(response.status_code, 404)

    async def test_api_create_user(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            user_create_response = await client.post(
                "/users",
                json={
                    "username": "test",
                    "password": "1234",
                    "age": 20,
                    "gender": "male",
                },
            )
        self.assertEqual(user_create_response.status_code, 200)

    async def test_api_get_token_by_login(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            await client.post(
                "/users",
                json={
                    "username": (username := "test"),
                    "password": (password := "1234"),
                    "age": 20,
                    "gender": "male",
                },
            )

            user = await client.post("/users/login", data={"username": username, "password": password})
        self.assertEqual(user.status_code, 200)
        response_body = user.json()
        self.assertIsNotNone(response_body["access_token"])

    async def test_api_get_user(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            user_create_response = await client.post(
                "/users",
                json={
                    "username": (username := "test"),
                    "password": (password := "1234"),
                    "age": (age := 20),
                    "gender": (gender := "male"),
                },
            )
            id = int(user_create_response.text)

            user = await client.post("/users/login", data={"username": username, "password": password})
            access_token = user.json()["access_token"]

            response_me = await client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response_me.status_code, 200)
        response_body = response_me.json()
        self.assertEqual(response_body["id"], id)
        self.assertEqual(response_body["username"], username)
        self.assertEqual(response_body["age"], age)
        self.assertEqual(response_body["gender"], gender)

    async def test_api_update_user(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            user_create_response = await client.post(
                "/users",
                json={
                    "username": (username := "test"),
                    "password": (password := "1234"),
                    "age": (age := 20),
                    "gender": (gender := "male"),
                },
            )
            id = int(user_create_response.text)

            login_user = await client.post("/users/login", data={"username": username, "password": password})
            access_token = login_user.json()["access_token"]

            response_me = await client.patch(
                "/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "username": (new_username := "new_username"),
                    "password": (new_password := "new_password"),
                    "age": (new_age := age + 1),
                },
            )
        self.assertEqual(response_me.status_code, 200)
        response_body = response_me.json()
        self.assertEqual(response_body["id"], id)
        self.assertEqual(response_body["username"], new_username)
        self.assertEqual(response_body["age"], new_age)
        self.assertEqual(response_body["gender"], gender)
        self.assertTrue(verify_password(new_password, (await User.get(id=id)).hashed_password))
