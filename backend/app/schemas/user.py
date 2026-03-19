import re
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,20}$")


class DashboardSummaryResponse(BaseModel):
    friends_count: int
    posts_count: int
    unread_notifications: int
    pending_requests: int


class DiscoverUserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    headline: str
    relationship_status: Literal["friend", "incoming_request", "outgoing_request", "none"]


class UpdateProfileRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    headline: str = Field(min_length=1, max_length=120)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        username = value.strip()
        if not USERNAME_RE.fullmatch(username):
            raise ValueError("Username must be 3-20 chars and use letters, numbers, underscores, or periods only")
        return username

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, value: str) -> str:
        headline = value.strip()
        if not headline:
            raise ValueError("Headline cannot be empty")
        return headline


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        has_upper = any(char.isupper() for char in value)
        has_lower = any(char.islower() for char in value)
        has_digit = any(char.isdigit() for char in value)
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Password must include uppercase, lowercase, and a number")
        return value


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
