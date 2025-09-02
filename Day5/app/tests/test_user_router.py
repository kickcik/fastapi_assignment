import os

import httpx
from dotenv import load_dotenv
from starlette import status
from tortoise.contrib.test import TestCase, finalizer, initializer

from Day5.app.configs import config
from Day5.app.main import app
from Day5.app.models.users import GenderName, User
from Day5.app.tests.utils.fake_file import fake_image, fake_txt_file
from Day5.app.utils.auth import verify_password
from Day5.app.utils.file import IMAGE_EXTENSIONS

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

    async def test_main_get_index(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/")
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body["message"], "Hello World")

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

    async def test_api_get_token_by_login_none(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            await client.post(
                "/users",
                json={
                    "username": (username := "login_none_test"),
                    "password": (password := "1234"),
                    "age": 20,
                    "gender": "male",
                },
            )
            user1 = await client.post(
                "/users/login",
                data={
                    "username": "fadsadsa",
                    "password": password,
                },
            )
            user2 = await client.post(
                "/users/login",
                data={
                    "username": username,
                    "password": "12345",
                },
            )

        self.assertEqual(user1.status_code, 401)
        response_body = user1.json()
        self.assertEqual(response_body["detail"], "username: fadsadsa - not found.")

        self.assertEqual(user2.status_code, 401)
        response_body = user2.json()
        self.assertEqual(response_body["detail"], "password incorrect.")

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

    async def test_api_delete_user(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            await client.post(
                "/users",
                json={
                    "username": (username := "test"),
                    "password": (password := "1234"),
                    "age": 20,
                    "gender": "male",
                },
            )

            login_user = await client.post("/users/login", data={"username": username, "password": password})
            access_token = login_user.json()["access_token"]

            response_me = await client.delete("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response_me.status_code, 200)
        response_body = response_me.json()
        self.assertEqual(response_body["detail"], "Successfully Deleted.")

    async def test_api_search_users(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            user_create_response = await client.post(
                "/users",
                json={
                    "username": (username := "test1"),
                    "password": "1234",
                    "age": (age := 20),
                    "gender": (gender := "male"),
                },
            )
            id = int(user_create_response.text)
            await client.post(
                "/users",
                json={
                    "username": "test2",
                    "password": "12345",
                    "age": 25,
                    "gender": "female",
                },
            )

            search_user_response = await client.get(
                "/users/search", params={"username": username, "age": age, "gender": gender}
            )
        self.assertEqual(search_user_response.status_code, 200)
        response_body = search_user_response.json()[0]
        self.assertEqual(response_body["id"], id)
        self.assertEqual(response_body["username"], username)
        self.assertEqual(response_body["age"], age)
        self.assertEqual(response_body["gender"], gender)

    async def test_api_search_users_none(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            await client.post(
                "/users",
                json={
                    "username": "test1",
                    "password": "1234",
                    "age": 20,
                    "gender": "male",
                },
            )
            await client.post(
                "/users",
                json={
                    "username": "test2",
                    "password": "12345",
                    "age": 25,
                    "gender": "female",
                },
            )

            search_user_response = await client.get(
                "/users/search", params={"username": "safvads", "age": 999, "gender": "male"}
            )
        self.assertEqual(search_user_response.status_code, 404)

    async def test_api_register_user_profile_image(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderName.male,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            login_user = await client.post("/users/login", data={"username": user.username, "password": password})
            access_token = login_user.json()["access_token"]

            # when
            response = await client.post(
                "/users/me/profile_image",
                files={"image": ((image := "test_image.png"), fake_image(), "image/png")},
                headers={"Authorization": f"Bearer {access_token}"},
            )

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()

        assert f"users/profile_images/{image.rsplit(".")[0]}" in response_json["profile_image_url"]
        assert image.rsplit(".")[1] in response_json["profile_image_url"]

        await user.refresh_from_db()
        assert response_json["profile_image_url"] == user.profile_image_url

        saved_file_path = os.path.join(config.MEDIA_DIR, user.profile_image_url)
        # 파일이 저장되었는지 확인
        assert os.path.exists(saved_file_path)

        # 리소스 정리
        os.remove(saved_file_path)

    async def test_api_register_user_profile_image_when_file_has_unavailable_extension(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderName.male,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            login_user = await client.post("/users/login", data={"username": user.username, "password": password})
            access_token = login_user.json()["access_token"]

            # when
            response = await client.post(
                "/users/me/profile_image",
                files={"image": ("test_file.txt", fake_txt_file(), "text/plain")},
                headers={"Authorization": f"Bearer {access_token}"},
            )

        # then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()

        assert response_json["detail"] == f"invalid image extension. enable extension: {IMAGE_EXTENSIONS}"

    async def test_api_register_profile_image_prev_url_not_none(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            create_user = await client.post(
                "/users",
                json={
                    "username": (username := "test_profile_image"),
                    "password": (password := "1234"),
                    "age": (age := 20),
                    "gender": (gender := "female"),
                },
            )
            id = int(create_user.text)
            user = await client.post("/users/login", data={"username": username, "password": password})
            access_token = user.json()["access_token"]

            await client.post(
                "/users/me/profile_image",
                files={"image": ("test_image.png", fake_image(), "image/png")},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response = await client.post(
                "/users/me/profile_image",
                files={"image": ("test_image.png", fake_image(), "image/png")},
                headers={"Authorization": f"Bearer {access_token}"},
            )
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body["id"], id)
        self.assertEqual(response_body["username"], username)
        self.assertEqual(response_body["age"], age)
        self.assertEqual(response_body["gender"], gender)
        self.assertIsNotNone(response_body["profile_image_url"])
