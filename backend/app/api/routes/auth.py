import os

from dotenv import load_dotenv

load_dotenv()
from fastapi import APIRouter, HTTPException

from app.core.security import decode_token, make_token
from app.models.schemas import LoginRequest, RefreshRequest, TokenPair
from app.services.store import ensure_user, refresh_tokens

router = APIRouter()
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
REFRESH_TOKEN_EXPIRES_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRES_MINUTES", str(24 * 7)))


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest) -> TokenPair:
    user = ensure_user(payload.email)
    access = make_token(
        user["id"],
        expires_minutes=ACCESS_TOKEN_EXPIRES_MINUTES,
        token_type="access",
        role=user["role"],
    )
    refresh = make_token(
        user["id"],
        expires_minutes=REFRESH_TOKEN_EXPIRES_MINUTES,
        token_type="refresh",
        role=user["role"],
    )
    refresh_tokens[refresh] = user["id"]
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest) -> TokenPair:
    if payload.refresh_token not in refresh_tokens:
        raise HTTPException(status_code=401, detail="Unknown refresh token")
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user_id = refresh_tokens.pop(payload.refresh_token)
    role = decoded.get("role", "user")
    next_access = make_token(
        user_id,
        expires_minutes=ACCESS_TOKEN_EXPIRES_MINUTES,
        token_type="access",
        role=role,
    )
    next_refresh = make_token(
        user_id,
        expires_minutes=REFRESH_TOKEN_EXPIRES_MINUTES,
        token_type="refresh",
        role=role,
    )
    refresh_tokens[next_refresh] = user_id
    return TokenPair(access_token=next_access, refresh_token=next_refresh)
