from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, require_roles
from app.core.object_id import parse_object_id
from app.db.mongodb import get_collection
from app.schemas.post import CreatePostRequest, PostResponse
from app.services.notifications import create_notification, get_friend_ids
from app.services.ws_manager import ws_manager

router = APIRouter(prefix="/posts", tags=["posts"])


async def _serialize_post(post: dict, current_user_id: str) -> PostResponse:
    users = get_collection("users")
    author = await users.find_one({"_id": parse_object_id(post["author_id"], "author_id")})

    reactions = post.get("reactions", [])
    counts: dict[str, int] = {}
    user_reaction = None
    for item in reactions:
        reaction_type = item["type"]
        counts[reaction_type] = counts.get(reaction_type, 0) + 1
        if item["user_id"] == current_user_id:
            user_reaction = reaction_type

    return PostResponse(
        id=str(post["_id"]),
        author_id=post["author_id"],
        author_username=author["username"] if author else "Unknown",
        author_headline=author.get("headline", "") if author else "",
        content=post["content"],
        created_at=post["created_at"],
        reactions=counts,
        total_reactions=sum(counts.values()),
        user_reaction=user_reaction,
    )


async def _ensure_post_visible(post: dict, current_user_id: str) -> None:
    if post["author_id"] == current_user_id:
        return

    friend_ids = await get_friend_ids(current_user_id)
    if post["author_id"] not in friend_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this post")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(payload: CreatePostRequest, user: dict = Depends(require_roles("user", "admin"))):
    posts = get_collection("posts")

    doc = {
        "author_id": user["id"],
        "content": payload.content,
        "reactions": [],
        "created_at": datetime.now(timezone.utc),
    }
    result = await posts.insert_one(doc)
    doc["_id"] = result.inserted_id

    friend_ids = await get_friend_ids(user["id"])
    for friend_id in friend_ids:
        await create_notification(
            friend_id,
            "new_post",
            f"{user['username']} published a new post",
            {"post_id": str(result.inserted_id), "author_id": user["id"]},
        )
        await ws_manager.send_personal(
            friend_id,
            {
                "event": "feed:new_post",
                "payload": {
                    "post_id": str(result.inserted_id),
                    "author_id": user["id"],
                    "author_username": user["username"],
                    "content": payload.content,
                    "created_at": doc["created_at"].isoformat(),
                },
            },
        )

    return await _serialize_post(doc, user["id"])


@router.get("/feed")
async def feed(limit: int = Query(default=20, ge=5, le=50), user: dict = Depends(get_current_user)):
    posts = get_collection("posts")
    friend_ids = await get_friend_ids(user["id"])
    allowed_authors = friend_ids + [user["id"]]

    cursor = posts.find({"author_id": {"$in": allowed_authors}}).sort("created_at", -1).limit(limit)
    items: list[PostResponse] = []
    async for post in cursor:
        items.append(await _serialize_post(post, user["id"]))
    return items


@router.post("/{post_id}/reactions/{reaction_type}")
async def react_to_post(post_id: str, reaction_type: str, user: dict = Depends(require_roles("user", "admin"))):
    allowed_reactions = {"like", "love", "haha", "wow", "sad", "angry"}
    if reaction_type not in allowed_reactions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported reaction")

    posts = get_collection("posts")
    post = await posts.find_one({"_id": parse_object_id(post_id, "post_id")})
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await _ensure_post_visible(post, user["id"])

    reactions = post.get("reactions", [])
    existing = next((r for r in reactions if r["user_id"] == user["id"]), None)

    if existing and existing["type"] == reaction_type:
        reactions = [r for r in reactions if r["user_id"] != user["id"]]
    elif existing:
        for r in reactions:
            if r["user_id"] == user["id"]:
                r["type"] = reaction_type
                break
    else:
        reactions.append({"user_id": user["id"], "type": reaction_type})

    await posts.update_one({"_id": parse_object_id(post_id, "post_id")}, {"$set": {"reactions": reactions}})

    if post["author_id"] != user["id"]:
        await create_notification(
            post["author_id"],
            "reaction",
            f"{user['username']} reacted to your post",
            {"post_id": post_id, "reaction_type": reaction_type, "reactor_id": user["id"]},
        )

    updated = await posts.find_one({"_id": parse_object_id(post_id, "post_id")})
    return await _serialize_post(updated, user["id"])
