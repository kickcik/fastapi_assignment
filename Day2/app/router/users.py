from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from Day2.app.models.users import UserModel
from Day2.app.schemas.users import (
    UserCreateSchema,
    UserResponse,
    UserSearchParams,
    UserUpdateSchema,
)

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")  # 유저 생성
def create_user(user: UserCreateSchema) -> int:

    new_user = UserModel(user.username, user.age, user.gender)
    return new_user.id


@user_router.get("", response_model=list[UserResponse])  # 유저 목록 조회
def get_users() -> list[UserResponse]:
    if user_list := [UserResponse.model_validate(user) for user in UserModel.all()]:
        return user_list
    else:

        raise HTTPException(status_code=404, detail="No users found")


@user_router.get("/{user_id}", response_model=UserResponse)  # 유저 정보 조회
def get_user(user_id: int = Path(gt=0)) -> UserResponse:
    if user := UserModel.get(id=user_id):
        return UserResponse.model_validate(user)
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.patch("/{user_id}", response_model=UserResponse)  # 유저 정보 갱신
def update_user(user_data: UserUpdateSchema, user_id: int = Path(gt=0)) -> UserResponse:
    if user := UserModel.get(id=user_id):
        # UserUpdateSchema로 변환된 객체를 model_dump()로 파이썬 딕셔너리로 변환 후 ** 언팩킹하여 키워드 인자로 변환
        user.update(**user_data.model_dump())
        return UserResponse.model_validate(user)
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.delete("/{user_id}")  # 유저 정보 삭제
def delete_user(user_id: int = Path(gt=0)) -> dict[str, str]:
    if user := UserModel.get(id=user_id):
        user.delete()
        return {"detail": f"User: {user_id}, Successfully Deleted."}
    else:
        raise HTTPException(status_code=404, detail="No users found")


@user_router.get("/search", response_model=list[UserResponse])  # 유저 검색
def search_users(params: Annotated[UserSearchParams, Query()]) -> list[UserResponse]:
    valid_query = {key: value for key, value in params.model_dump().items() if value is not None}
    if filtered_user_list := UserModel.filter(**valid_query):
        return [UserResponse.model_validate(user) for user in filtered_user_list]
    else:
        raise HTTPException(status_code=404, detail="No users found")
