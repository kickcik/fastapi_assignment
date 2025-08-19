from enum import Enum

from pydantic import BaseModel


class GenderName(str, Enum):
    male = "male"
    female = "female"


class UserCreateSchema(BaseModel):
    username: str
    age: int
    gender: GenderName


class UserUpdateSchema(BaseModel):
    username: str | None = None
    age: int | None = None
    gender: GenderName | None = None


class UserSearchParams(BaseModel):
    model_config = {"extra": "forbid"}

    username: str | None = None
    age: int | None = None
    gender: GenderName | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    age: int
    gender: GenderName

    model_config = {"from_attributes": True}  # from_orm 대신
