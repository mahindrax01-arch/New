from typing import Literal

from pydantic import BaseModel, field_validator, model_validator


class FriendRequestCreate(BaseModel):
    receiver_id: str | None = None
    identifier: str | None = None

    @field_validator("receiver_id")
    @classmethod
    def normalize_receiver_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        return normalized or None

    @model_validator(mode="after")
    def validate_target(self):
        if not self.receiver_id and not self.identifier:
            raise ValueError("Provide either a receiver_id or an identifier")
        return self


class FriendRequestRespond(BaseModel):
    action: Literal["accept", "reject"]
