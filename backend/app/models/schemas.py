from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    guest = "guest"
    user = "user"
    admin = "admin"


class User(BaseModel):
    id: str
    email: str
    role: Role = Role.user


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class LoginRequest(BaseModel):
    email: str


class RefreshRequest(BaseModel):
    refresh_token: str


class PostCreate(BaseModel):
    text: str = Field(min_length=1, max_length=280)


class Post(BaseModel):
    id: str
    author_id: str
    text: str
    reactions: dict[str, int] = Field(default_factory=dict)
