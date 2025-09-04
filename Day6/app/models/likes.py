from tortoise import Model, fields

from Day6.app.models.base import BaseModel
from Day6.app.models.reviews import Review
from Day6.app.models.users import User


class ReviewLike(BaseModel, Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", related_name="review_likes")
    review: fields.ForeignKeyRelation[Review] = fields.ForeignKeyField("models.Review", related_name="likes")
    is_liked = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "review_likes"
        unique_together = (("user", "review"),)
