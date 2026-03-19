from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.object_id import parse_object_id
from app.db.mongodb import get_collection

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(user: dict = Depends(get_current_user)):
    notifications = get_collection("notifications")
    items = []
    async for item in notifications.find({"user_id": user["id"]}).sort("created_at", -1).limit(100):
        items.append(
            {
                "id": str(item["_id"]),
                "user_id": item["user_id"],
                "type": item["type"],
                "message": item["message"],
                "data": item.get("data", {}),
                "is_read": item.get("is_read", False),
                "created_at": item["created_at"],
            }
        )
    return items


@router.patch("/{notification_id}/read")
async def mark_read(notification_id: str, user: dict = Depends(get_current_user)):
    notifications = get_collection("notifications")
    result = await notifications.update_one(
        {"_id": parse_object_id(notification_id, "notification_id"), "user_id": user["id"]},
        {"$set": {"is_read": True}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"ok": True}


@router.patch("/read-all")
async def mark_all_read(user: dict = Depends(get_current_user)):
    notifications = get_collection("notifications")
    await notifications.update_many({"user_id": user["id"], "is_read": False}, {"$set": {"is_read": True}})
    return {"ok": True}
