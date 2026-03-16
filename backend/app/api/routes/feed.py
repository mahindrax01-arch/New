from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, require_role
from app.models.schemas import Post, PostCreate
from app.services.store import posts

router = APIRouter()


@router.get("", response_model=list[Post])
def list_feed() -> list[Post]:
    return list(reversed(posts))


@router.post("", response_model=Post)
def create_post(payload: PostCreate, user: dict = Depends(get_current_user)) -> Post:
    require_role(user, {"user", "admin"})
    post = Post(id=str(uuid4()), author_id=user["id"], text=payload.text)
    posts.append(post)
    return post


@router.post("/{post_id}/react/{emoji}", response_model=Post)
def react(post_id: str, emoji: str, user: dict = Depends(get_current_user)) -> Post:
    require_role(user, {"user", "admin"})
    for idx, post in enumerate(posts):
        if post.id == post_id:
            updated = post.model_copy(deep=True)
            updated.reactions[emoji] = updated.reactions.get(emoji, 0) + 1
            posts[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Post not found")
