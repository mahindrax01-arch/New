from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_role
from app.services.store import friends

router = APIRouter()


@router.post("/{target_user_id}")
def add_friend(target_user_id: str, user: dict = Depends(get_current_user)) -> dict:
    require_role(user, {"user", "admin"})
    friends[user["id"]].add(target_user_id)
    friends[target_user_id].add(user["id"])
    return {"ok": True, "friend_count": len(friends[user["id"]])}
