from enum import StrEnum
from typing import Any, Dict, List

from tortoise import Model, fields

from Day6.app.models.base import BaseModel


class GenreEnum(StrEnum):
    SF = "SF"
    ADVENTURE = "Adventure"
    ROMANCE = "Romance"
    COMIC = "Comic"
    FANTASY = "Fantasy"
    SCIENCE = "Science"
    MYSTERY = "Mystery"
    ACTION = "Action"
    HORROR = "Horror"


class Movie(BaseModel, Model):
    title = fields.CharField(max_length=255)
    plot = fields.TextField()
    cast: List[Dict[str, Any]] = fields.JSONField()
    playtime = fields.IntField()
    genre = fields.CharEnumField(GenreEnum)
    poster_image_url = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "movies"
