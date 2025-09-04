from tortoise import Model, fields

from Day6.app.models.base import BaseModel
from Day6.app.models.movies import Movie
from Day6.app.models.users import User


class Review(BaseModel, Model):
    title = fields.CharField(max_length=50, null=False)
    content = fields.TextField(max_length=255, null=False)
    review_image_url = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="reviews", on_delete=fields.CASCADE
    )
    movie: fields.ForeignKeyRelation[Movie] = fields.ForeignKeyField(
        "models.Movie", related_name="reviews", on_delete=fields.CASCADE
    )

    class Meta:
        table = "reviews"
        unique_together = (("user", "movie"),)
