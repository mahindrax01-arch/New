from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, require_roles
from app.core.object_id import parse_object_id
from app.db.mongodb import get_collection
from app.schemas.friend import FriendRequestCreate, FriendRequestRespond
from app.services.notifications import create_notification

router = APIRouter(prefix="/friends", tags=["friends"])


async def _resolve_receiver(payload: FriendRequestCreate) -> tuple[str, dict]:
    users = get_collection("users")

    if payload.receiver_id:
        receiver = await users.find_one({"_id": parse_object_id(payload.receiver_id, "receiver_id")})
        if not receiver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        return payload.receiver_id, receiver

    assert payload.identifier is not None
    receiver = await users.find_one(
        {
            "$or": [
                {"username_lower": payload.identifier},
                {"email": payload.identifier},
            ]
        }
    )
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user matched that username or email")
    return str(receiver["_id"]), receiver


@router.post("/requests", status_code=status.HTTP_201_CREATED)
async def send_friend_request(payload: FriendRequestCreate, user: dict = Depends(require_roles("user", "admin"))):
    receiver_id, receiver = await _resolve_receiver(payload)
    if receiver_id == user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send a friend request to yourself")

    requests = get_collection("friend_requests")
    friendships = get_collection("friendships")

    existing_friendship = await friendships.find_one({"users": {"$all": [user["id"], receiver_id]}})
    if existing_friendship:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already friends")

    existing_request = await requests.find_one(
        {
            "$or": [
                {"sender_id": user["id"], "receiver_id": receiver_id, "status": "pending"},
                {"sender_id": receiver_id, "receiver_id": user["id"], "status": "pending"},
            ]
        }
    )
    if existing_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pending request already exists")

    doc = {
        "sender_id": user["id"],
        "receiver_id": receiver_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
    }
    result = await requests.insert_one(doc)

    await create_notification(
        receiver_id,
        "friend_request",
        f"{user['username']} sent you a friend request",
        {"request_id": str(result.inserted_id), "sender_id": user["id"]},
    )

    return {"id": str(result.inserted_id), **doc}


@router.patch("/requests/{request_id}")
async def respond_friend_request(
    request_id: str,
    payload: FriendRequestRespond,
    user: dict = Depends(require_roles("user", "admin")),
):
    if payload.action not in {"accept", "reject"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    requests = get_collection("friend_requests")
    friendships = get_collection("friendships")

    req = await requests.find_one({"_id": parse_object_id(request_id, "request_id")})
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if req["receiver_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if req["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Request already processed")

    new_status = "accepted" if payload.action == "accept" else "rejected"
    await requests.update_one(
        {"_id": parse_object_id(request_id, "request_id")},
        {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}},
    )

    if payload.action == "accept":
        users_pair = sorted([req["sender_id"], req["receiver_id"]])
        await friendships.update_one(
            {"pair_key": ":".join(users_pair)},
            {
                "$setOnInsert": {
                    "users": users_pair,
                    "pair_key": ":".join(users_pair),
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
        await create_notification(
            req["sender_id"],
            "friend_accept",
            f"{user['username']} accepted your friend request",
            {"friend_id": user["id"]},
        )

    return {"ok": True, "status": new_status}


@router.delete("/requests/{request_id}")
async def cancel_friend_request(request_id: str, user: dict = Depends(require_roles("user", "admin"))):
    requests = get_collection("friend_requests")

    req = await requests.find_one({"_id": parse_object_id(request_id, "request_id")})
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if req["sender_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if req["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending requests can be cancelled")

    await requests.update_one(
        {"_id": parse_object_id(request_id, "request_id")},
        {"$set": {"status": "cancelled", "updated_at": datetime.now(timezone.utc)}},
    )
    return {"ok": True, "status": "cancelled"}


@router.get("")
async def list_friends(user: dict = Depends(get_current_user)):
    friendships = get_collection("friendships")
    users = get_collection("users")

    result = []
    async for item in friendships.find({"users": user["id"]}):
        friend_id = item["users"][0] if item["users"][1] == user["id"] else item["users"][1]
        friend = await users.find_one({"_id": parse_object_id(friend_id, "friend_id")})
        if friend:
            result.append(
                {
                    "id": str(friend["_id"]),
                    "username": friend["username"],
                    "email": friend["email"],
                    "headline": friend.get("headline", ""),
                }
            )

    return result


@router.get("/requests/pending")
async def pending_requests(user: dict = Depends(get_current_user)):
    requests = get_collection("friend_requests")
    users = get_collection("users")
    incoming = []

    async for req in requests.find({"receiver_id": user["id"], "status": "pending"}).sort("created_at", -1):
        sender = await users.find_one({"_id": parse_object_id(req["sender_id"], "sender_id")})
        incoming.append(
            {
                "id": str(req["_id"]),
                "sender_id": req["sender_id"],
                "sender_username": sender["username"] if sender else "Unknown",
                "sender_headline": sender.get("headline", "") if sender else "",
                "created_at": req["created_at"],
            }
        )

    return incoming


@router.get("/requests/outgoing")
async def outgoing_requests(user: dict = Depends(get_current_user)):
    requests = get_collection("friend_requests")
    users = get_collection("users")
    outgoing = []

    async for req in requests.find({"sender_id": user["id"], "status": "pending"}).sort("created_at", -1):
        receiver = await users.find_one({"_id": parse_object_id(req["receiver_id"], "receiver_id")})
        outgoing.append(
            {
                "id": str(req["_id"]),
                "receiver_id": req["receiver_id"],
                "receiver_username": receiver["username"] if receiver else "Unknown",
                "receiver_headline": receiver.get("headline", "") if receiver else "",
                "created_at": req["created_at"],
            }
        )

    return outgoing
