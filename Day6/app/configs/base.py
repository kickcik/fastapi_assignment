import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")

    JWT_ALGORITHM: str | None = os.getenv("JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))  # type: ignore[arg-type]

    MYSQL_HOST: str | None = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str | None = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str | None = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB: str | None = os.getenv("MYSQL_DB")

    MYSQL_CONNECT_TIMEOUT: int = 5
    CONNECTION_POOL_MAXSIZE: int = 10

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MEDIA_DIR: str = os.path.join(BASE_DIR, "media")
