from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    public_key: str | None = None
    encrypted_private_key: str | None = None
    private_key_salt: str | None = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class SessionUser(BaseModel):
    id: str
    email: EmailStr
    username: str
    name: str
    avatar_url: str | None = None
    bio: str | None = None
    public_key: str | None = None
    encrypted_private_key: str | None = None
    private_key_salt: str | None = None
    theme: str
    is_online: bool
