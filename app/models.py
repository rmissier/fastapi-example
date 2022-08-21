from tortoise import Tortoise, fields, models


class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class User(TimestampMixin, models.Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, default="", null=False)
    email = fields.CharField(max_length=100, index=True, unique=True, null=False)
    password = fields.CharField(max_length=100, null=False)
    disabled = fields.BooleanField(default=False)
    posts: fields.ReverseRelation["Post"]
    votes: fields.ReverseRelation["Post"]

    def __repr__(self):
        return f"User({self.id}, {self.email}, {self.disabled})"

    class PydanticMeta:
        exclude = ("password",)


class Post(TimestampMixin, models.Model):
    id = fields.IntField(pk=True, index=True)
    title = fields.CharField(max_length=100, null=False)
    content = fields.TextField(null=False)
    published = fields.BooleanField(default=False)
    author: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="posts", on_delete=fields.CASCADE, null=False, index=True
    )
    votes: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User", related_name="votes", on_delete=fields.CASCADE, null=False, index=True
    )

    def __repr__(self):
        return f'Post({self.id}, "{self.title}", {self.content}, ...)'


Tortoise.init_models(["app.models"], "models")
