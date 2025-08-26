from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from Day5.app.models.users import User
from Day5.app.schemas.users import (
    Token,
    UserCreateSchema,
    UserResponse,
    UserSearchParams,
    UserUpdateSchema,
)
from Day4.app.utils.auth import authenticate, get_current_user, hash_password
from Day4.app.utils.jwt import create_access_token

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")  # 유저 생성
async def create_user(data: UserCreateSchema) -> int:
    user_data = data.model_dump()
    user_data["hashed_password"] = hash_password(user_data.pop("password"))
    new_user = await User.create(**user_data)
    return new_user.id


@user_router.get("", response_model=list[UserResponse])  # 유저 목록 조회
async def get_all_users() -> list[User]:
    if user_list := await User.filter().all():
        return user_list
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.get("/me", response_model=UserResponse)  # 유저 정보 조회
async def get_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@user_router.patch("/me", response_model=UserResponse)  # 유저 정보 갱신
async def update_user(user: Annotated[User, Depends(get_current_user)], user_data: UserUpdateSchema) -> UserResponse:
    update_data = {key: value for key, value in user_data.model_dump().items() if value is not None}
    if "password" in update_data.keys():
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    user = await user.update_from_dict(data=update_data)
    await user.save()
    return UserResponse.model_validate(user)


@user_router.delete("/me")  # 유저 정보 삭제
async def delete_user(user: Annotated[User, Depends(get_current_user)]) -> dict[str, str]:
    await user.delete()
    return {"detail": "Successfully Deleted."}


@user_router.get("/search", response_model=list[UserResponse])  # 유저 검색
async def search_users(params: Annotated[UserSearchParams, Query()]) -> list[User]:
    valid_query = {key: value for key, value in params.model_dump().items() if value is not None}
    if filtered_user_list := await User.filter(**valid_query).all():
        return filtered_user_list
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"user_id": user.id})
    user.last_login = datetime.now()
    await user.save()
    return Token(access_token=access_token, token_type="bearer")
