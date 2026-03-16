from collections import defaultdict
from uuid import uuid4

from app.models.schemas import Post

users_by_email: dict[str, dict] = {}
refresh_tokens: dict[str, str] = {}
posts: list[Post] = []
friends: dict[str, set[str]] = defaultdict(set)


def ensure_user(email: str) -> dict:
    if email not in users_by_email:
        user_id = str(uuid4())
        role = "admin" if email.endswith("@admin.local") else "user"
        users_by_email[email] = {"id": user_id, "email": email, "role": role}
    return users_by_email[email]
