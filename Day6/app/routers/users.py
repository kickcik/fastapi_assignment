from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from Day6.app.models.users import User
from Day6.app.schemas.users import (
    Token,
    UserCreateSchema,
    UserResponse,
    UserSearchParams,
    UserUpdateSchema,
)
from Day6.app.utils.auth import authenticate, get_current_user, hash_password
from Day6.app.utils.file import delete_file, upload_file, validate_image_extension
from Day6.app.utils.jwt import create_access_token

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

    access_token = create_access_token(data={"user_id": user.id})
    user.last_login = datetime.now()
    await user.save()
    return Token(access_token=access_token, token_type="bearer")


@user_router.post("/me/profile_image", status_code=200)
async def register_profile_image(image: UploadFile, user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    validate_image_extension(image)
    prev_image_url = user.profile_image_url
    try:
        image_url = await upload_file(image, "users/profile_images")
        user.profile_image_url = image_url
        await user.save()

        if prev_image_url is not None:
            delete_file(prev_image_url)

        return UserResponse(
            id=user.id,
            username=user.username,
            age=user.age,
            gender=user.gender,
            profile_image_url=user.profile_image_url,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
