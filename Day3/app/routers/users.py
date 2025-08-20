from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from Day3.app.models.users import UserModel
from Day3.app.schemas.users import (
    Token,
    UserCreateSchema,
    UserResponse,
    UserSearchParams,
    UserUpdateSchema,
)
from Day3.app.utils.jwt import create_access_token, get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")  # 유저 생성
def create_user(user: UserCreateSchema) -> int:
    new_user = UserModel(user.username, user.password, user.age, user.gender)
    return new_user.id


@user_router.get("", response_model=list[UserResponse])  # 유저 목록 조회
def get_users() -> list[UserResponse]:
    if user_list := [UserResponse.model_validate(user) for user in UserModel.all()]:
        return user_list
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.get("/me", response_model=UserResponse)  # 유저 정보 조회
async def get_user(user: Annotated[UserModel, Depends(get_current_user)]) -> UserModel:
    return user


@user_router.patch("/me", response_model=UserResponse)  # 유저 정보 갱신
def update_user(user: Annotated[UserModel, Depends(get_current_user)], user_data: UserUpdateSchema) -> UserModel:
    # UserUpdateSchema로 변환된 객체를 model_dump()로 파이썬 딕셔너리로 변환 후 ** 언팩킹하여 키워드 인자로 변환
    user.update(**user_data.model_dump())
    return user


@user_router.delete("/me")  # 유저 정보 삭제
def delete_user(user: Annotated[UserModel, Depends(get_current_user)]) -> dict[str, str]:
    user.delete()
    return {"detail": "Successfully Deleted."}


@user_router.get("/search", response_model=list[UserResponse])  # 유저 검색
def search_users(params: Annotated[UserSearchParams, Query()]) -> list[UserResponse]:
    valid_query = {key: value for key, value in params.model_dump().items() if value is not None}
    if filtered_user_list := UserModel.filter(**valid_query):
        return [UserResponse.model_validate(user) for user in filtered_user_list]
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = UserModel.authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"user_id": user.id})
    user.update(last_login=datetime.now())
    return Token(access_token=access_token, token_type="bearer")
