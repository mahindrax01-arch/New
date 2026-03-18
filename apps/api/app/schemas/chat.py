from datetime import datetime

from pydantic import BaseModel, Field


class UserSummary(BaseModel):
    id: str
    name: str
    username: str
    avatar_url: str | None = None
    is_online: bool
    last_seen_at: datetime | None = None


class SecretKeyPayload(BaseModel):
    recipient_id: str
    wrapped_key: str
    signature: str | None = None


class MessageCreate(BaseModel):
    conversation_id: str
    body: str = Field(min_length=1, max_length=10000)
    plaintext_fallback: str | None = Field(default=None, max_length=4000)
    kind: str = 'text'
    reply_to_message_id: str | None = None
    client_nonce: str | None = Field(default=None, max_length=80)
    secret_keys: list[SecretKeyPayload] = []


class ReactionCreate(BaseModel):
    emoji: str = Field(min_length=1, max_length=16)


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=400)
    member_ids: list[str] = Field(min_length=1)
    is_secret: bool = False
    kind: str = 'direct'


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender: UserSummary
    body: str
    plaintext_fallback: str | None = None
    kind: str
    reply_to_message_id: str | None = None
    created_at: datetime
    edited_at: datetime | None = None
    reactions: dict[str, int] = {}
    secret_keys: list[SecretKeyPayload] = []


class ConversationResponse(BaseModel):
    id: str
    title: str | None
    kind: str
    description: str | None
    is_secret: bool
    avatar_url: str | None
    members: list[UserSummary]
    last_message: MessageResponse | None = None
    unread_count: int = 0


class TypingPayload(BaseModel):
    conversation_id: str
    is_typing: bool


class PresencePayload(BaseModel):
    user_id: str
    is_online: bool
    last_seen_at: datetime | None = None
