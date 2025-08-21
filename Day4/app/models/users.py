from enum import Enum

from tortoise import Model, fields

from Day4.app.models.base import BaseModel


class GenderName(str, Enum):
    male = "male"
    female = "female"


class User(BaseModel, Model):
    username = fields.CharField(unique=True, max_length=50)
    hashed_password = fields.CharField(max_length=255)
    age = fields.IntField()
    gender = fields.CharEnumField(GenderName)
    last_login = fields.DatetimeField(null=True)

    class Meta:
        table = "users"
