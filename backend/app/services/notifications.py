from datetime import datetime, timezone

from bson import ObjectId

from app.db.mongodb import get_collection
from app.services.ws_manager import ws_manager


async def create_notification(user_id: str, kind: str, message: str, data: dict | None = None) -> dict:
    notifications = get_collection("notifications")
    doc = {
        "user_id": user_id,
        "type": kind,
        "message": message,
        "data": data or {},
        "is_read": False,
        "created_at": datetime.now(timezone.utc),
    }
    result = await notifications.insert_one(doc)
    doc["_id"] = result.inserted_id
    payload = {
        "id": str(doc["_id"]),
        "type": doc["type"],
        "message": doc["message"],
        "data": doc["data"],
        "is_read": doc["is_read"],
        "created_at": doc["created_at"].isoformat(),
    }
    await ws_manager.send_personal(user_id, {"event": "notification", "payload": payload})
    return payload


async def get_friend_ids(user_id: str) -> list[str]:
    friendships = get_collection("friendships")
    cursor = friendships.find({"users": user_id})
    friend_ids: list[str] = []
    async for item in cursor:
        users = item.get("users", [])
        other = users[0] if users[1] == user_id else users[1]
        friend_ids.append(other)
    return friend_ids
