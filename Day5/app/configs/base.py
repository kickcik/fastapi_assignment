import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")

    JWT_ALGORITHM: str | None = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int | None = 30

    MYSQL_HOST: str | None = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str | None = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str | None = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB: str | None = os.getenv("MYSQL_DB")

    MYSQL_CONNECT_TIMEOUT: int = 5
    CONNECTION_POOL_MAXSIZE: int = 10
