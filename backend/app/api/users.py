import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.mongodb import get_collection
from app.schemas.auth import UserResponse
from app.schemas.user import (
    ChangePasswordRequest,
    DashboardSummaryResponse,
    DeleteAccountRequest,
    DiscoverUserResponse,
    UpdateProfileRequest,
)
from app.services.account_cleanup import delete_user_account_data

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/dashboard", response_model=DashboardSummaryResponse)
async def dashboard_summary(user: dict = Depends(get_current_user)):
    friendships = get_collection("friendships")
    posts = get_collection("posts")
    notifications = get_collection("notifications")
    friend_requests = get_collection("friend_requests")

    friends_count = await friendships.count_documents({"users": user["id"]})
    posts_count = await posts.count_documents({"author_id": user["id"]})
    unread_notifications = await notifications.count_documents({"user_id": user["id"], "is_read": False})
    pending_requests = await friend_requests.count_documents({"receiver_id": user["id"], "status": "pending"})

    return DashboardSummaryResponse(
        friends_count=friends_count,
        posts_count=posts_count,
        unread_notifications=unread_notifications,
        pending_requests=pending_requests,
    )


@router.get("/discover", response_model=list[DiscoverUserResponse])
async def discover_users(
    q: str = Query(default="", max_length=30),
    limit: int = Query(default=8, ge=1, le=20),
    user: dict = Depends(get_current_user),
):
    users = get_collection("users")
    friendships = get_collection("friendships")
    friend_requests = get_collection("friend_requests")

    friend_ids: set[str] = set()
    async for friendship in friendships.find({"users": user["id"]}):
        pair = friendship["users"]
        friend_ids.add(pair[0] if pair[1] == user["id"] else pair[1])

    outgoing_request_ids: set[str] = set()
    async for request in friend_requests.find({"sender_id": user["id"], "status": "pending"}):
        outgoing_request_ids.add(request["receiver_id"])

    incoming_request_ids: set[str] = set()
    async for request in friend_requests.find({"receiver_id": user["id"], "status": "pending"}):
        incoming_request_ids.add(request["sender_id"])

    filters: dict = {"_id": {"$ne": user["_id"]}}
    query = q.strip()
    if query:
        escaped = re.escape(query.lower())
        filters["$or"] = [
            {"username_lower": {"$regex": escaped}},
            {"email": {"$regex": escaped}},
        ]

    cursor = users.find(filters).sort("created_at", -1).limit(limit)

    items: list[DiscoverUserResponse] = []
    async for candidate in cursor:
        candidate_id = str(candidate["_id"])
        relationship_status = "none"
        if candidate_id in friend_ids:
            relationship_status = "friend"
        elif candidate_id in outgoing_request_ids:
            relationship_status = "outgoing_request"
        elif candidate_id in incoming_request_ids:
            relationship_status = "incoming_request"

        items.append(
            DiscoverUserResponse(
                id=candidate_id,
                username=candidate["username"],
                email=candidate["email"],
                role=candidate["role"],
                headline=candidate.get("headline", ""),
                relationship_status=relationship_status,
            )
        )

    return items


@router.patch("/me/profile", response_model=UserResponse)
async def update_profile(payload: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    users = get_collection("users")
    updates = {
        "headline": payload.headline,
        "updated_at": datetime.now(timezone.utc),
    }

    current_username_lower = user.get("username_lower", user["username"].lower())
    if payload.username and payload.username.lower() != current_username_lower:
        existing = await users.find_one({"username_lower": payload.username.lower()})
        if existing and str(existing["_id"]) != user["id"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")
        updates["username"] = payload.username
        updates["username_lower"] = payload.username.lower()

    await users.update_one({"_id": user["_id"]}, {"$set": updates})
    refreshed = await users.find_one({"_id": user["_id"]})
    assert refreshed is not None
    return UserResponse(
        id=str(refreshed["_id"]),
        email=refreshed["email"],
        username=refreshed["username"],
        role=refreshed["role"],
        headline=refreshed.get("headline", ""),
    )


@router.post("/me/password")
async def change_password(payload: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    users = get_collection("users")
    refresh_tokens = get_collection("refresh_tokens")
    db_user = await users.find_one({"_id": user["_id"]})
    if not db_user or not verify_password(payload.current_password, db_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": hash_password(payload.new_password), "updated_at": datetime.now(timezone.utc)}},
    )
    await refresh_tokens.update_many({"user_id": user["id"]}, {"$set": {"revoked": True}})
    return {"ok": True}


@router.delete("/me")
async def delete_account(payload: DeleteAccountRequest, user: dict = Depends(get_current_user)):
    users = get_collection("users")
    db_user = await users.find_one({"_id": user["_id"]})
    if not db_user or not verify_password(payload.password, db_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect")

    await delete_user_account_data(user["id"])
    return {"ok": True}
