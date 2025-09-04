from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError
from passlib.context import CryptContext  # type: ignore
from starlette import status

from Day6.app.configs import config
from Day6.app.models.users import User
from Day6.app.utils.jwt import oauth2_scheme

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        assert config.JWT_ALGORITHM is not None
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])  # type: ignore[arg-type]
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        credentials_exception.detail = "Invalid token."
        raise credentials_exception
    user = await User.get(id=user_id)
    if user is None:
        credentials_exception.detail = "User not found."
        raise credentials_exception
    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # type: ignore


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore


async def authenticate(username: str, password: str) -> User:
    user = await User.get_or_none(username=username)
    if user is None:
        raise HTTPException(status_code=401, detail=f"username: {username} - not found.")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="password incorrect.")
    return user
