from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CreatePostRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1200)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("Post cannot be empty")
        return content


class PostResponse(BaseModel):
    id: str
    author_id: str
    author_username: str
    author_headline: str
    content: str
    created_at: datetime
    reactions: dict[str, int]
    total_reactions: int
    user_reaction: str | None = None
