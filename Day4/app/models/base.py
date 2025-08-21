from tortoise import fields


class BaseModel:
    id = fields.IntField(primary_key=True, AutoIncrement=True)
    created_at = fields.DatetimeField(auto_now_add=True)
