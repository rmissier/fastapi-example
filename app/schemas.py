from typing import Optional

from pydantic import BaseModel, EmailStr  # pylint: disable=no-name-in-module
from tortoise.contrib.pydantic import pydantic_model_creator  # type: ignore
from tortoise.contrib.pydantic import pydantic_queryset_creator  # type: ignore

from .models import Post, User

UserRead = pydantic_model_creator(User)
UserReadList = pydantic_queryset_creator(User)  # type: ignore


class UserCreate(BaseModel):
    name: str = ""
    email: EmailStr
    password: str
    disabled: bool = False


class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    disabled: Optional[bool]

    class Config:
        arbitrary_types_allowed = True


PostRead = pydantic_model_creator(Post)


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = False


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None
