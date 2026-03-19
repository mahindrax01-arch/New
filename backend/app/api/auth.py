from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, require_roles
from app.core.object_id import parse_object_id
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.mongodb import get_collection
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPairResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(payload: RegisterRequest):
    users = get_collection("users")

    existing = await users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    existing_username = await users.find_one({"username_lower": payload.username.lower()})
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")

    doc = {
        "email": payload.email,
        "username": payload.username,
        "username_lower": payload.username.lower(),
        "password_hash": hash_password(payload.password),
        "headline": "Sharing updates with close friends.",
        "role": "user",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await users.insert_one(doc)

    return UserResponse(
        id=str(result.inserted_id),
        email=doc["email"],
        username=doc["username"],
        role=doc["role"],
        headline=doc["headline"],
    )


@router.post("/login", response_model=TokenPairResponse)
async def login(payload: LoginRequest):
    users = get_collection("users")
    refresh_tokens = get_collection("refresh_tokens")

    user = await users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.get("is_active", True) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")

    user_id = str(user["_id"])
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    await refresh_tokens.insert_one(
        {
            "jti": refresh["jti"],
            "family": refresh["family"],
            "user_id": user_id,
            "revoked": False,
            "replaced_by": None,
            "expires_at": datetime.fromtimestamp(refresh["exp"], tz=timezone.utc),
            "created_at": datetime.now(timezone.utc),
        }
    )
    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": datetime.now(timezone.utc)}},
    )

    return TokenPairResponse(access_token=access["token"], refresh_token=refresh["token"])


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(payload: RefreshRequest):
    refresh_tokens = get_collection("refresh_tokens")

    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = decoded.get("jti")
    family = decoded.get("family")
    user_id = decoded.get("sub")

    token_doc = await refresh_tokens.find_one({"jti": jti})
    if not token_doc:
        await refresh_tokens.update_many({"family": family}, {"$set": {"revoked": True}})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh reuse detected")

    if token_doc.get("revoked"):
        await refresh_tokens.update_many({"family": family}, {"$set": {"revoked": True}})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    now = datetime.now(timezone.utc)
    if token_doc["expires_at"] < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id, family=family)

    await refresh_tokens.update_one(
        {"jti": jti},
        {"$set": {"revoked": True, "replaced_by": new_refresh["jti"], "rotated_at": now}},
    )

    await refresh_tokens.insert_one(
        {
            "jti": new_refresh["jti"],
            "family": new_refresh["family"],
            "user_id": user_id,
            "revoked": False,
            "replaced_by": None,
            "expires_at": datetime.fromtimestamp(new_refresh["exp"], tz=timezone.utc),
            "created_at": now,
        }
    )

    return TokenPairResponse(access_token=new_access["token"], refresh_token=new_refresh["token"])


@router.post("/logout")
async def logout(payload: RefreshRequest):
    refresh_tokens = get_collection("refresh_tokens")
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError:
        return {"ok": True}
    if decoded.get("type") == "refresh":
        await refresh_tokens.update_many({"family": decoded.get("family")}, {"$set": {"revoked": True}})
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
async def me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        role=user["role"],
        headline=user.get("headline", ""),
    )


@router.patch("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, _: dict = Depends(require_roles("admin"))):
    allowed = {"guest", "user", "admin"}
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    users = get_collection("users")
    result = await users.update_one({"_id": parse_object_id(user_id, "user_id")}, {"$set": {"role": role}})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"ok": True, "role": role}
