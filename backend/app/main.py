import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from app.api import auth, friends, notifications, posts, users, ws
from app.core.config import get_settings
from app.core.middleware import RateLimitMiddleware, RateLimitRule, SecurityHeadersMiddleware
from app.db.mongodb import get_collection

settings = get_settings()
app = FastAPI(title=settings.app_name)
logger = logging.getLogger(__name__)

app.add_middleware(GZipMiddleware, minimum_size=512)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    rules=[
        RateLimitRule("/api/auth/login", frozenset({"POST"}), settings.auth_rate_limit_per_minute, 60),
        RateLimitRule("/api/auth/register", frozenset({"POST"}), settings.auth_rate_limit_per_minute, 60),
        RateLimitRule("/api/auth/refresh", frozenset({"POST"}), settings.auth_rate_limit_per_minute, 60),
        RateLimitRule("/api/posts", frozenset({"POST"}), settings.write_rate_limit_per_minute, 60),
        RateLimitRule("/api/friends/requests", frozenset({"POST", "PATCH"}), settings.write_rate_limit_per_minute, 60),
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(ws.router)


@app.on_event("startup")
async def startup_indexes():
    users = get_collection("users")
    refresh_tokens = get_collection("refresh_tokens")
    friend_requests = get_collection("friend_requests")
    friendships = get_collection("friendships")
    posts = get_collection("posts")
    notifications = get_collection("notifications")

    async for user in users.find({"username_lower": {"$exists": False}}):
        await users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "username_lower": user["username"].lower(),
                    "headline": user.get("headline", "Sharing updates with close friends."),
                }
            },
        )

    async for friendship in friendships.find({"pair_key": {"$exists": False}}):
        users_pair = sorted(friendship.get("users", []))
        if len(users_pair) == 2:
            await friendships.update_one(
                {"_id": friendship["_id"]},
                {"$set": {"users": users_pair, "pair_key": ":".join(users_pair)}},
            )

    await users.create_index("email", unique=True)
    await users.create_index("username_lower", unique=True)
    await refresh_tokens.create_index("jti", unique=True)
    await refresh_tokens.create_index("family")
    await friend_requests.create_index([("sender_id", 1), ("receiver_id", 1), ("status", 1)])
    await friend_requests.create_index([("receiver_id", 1), ("status", 1), ("created_at", -1)])
    await friend_requests.create_index([("sender_id", 1), ("status", 1), ("created_at", -1)])
    try:
        await friendships.drop_index("users_1")
    except Exception:
        pass
    await friendships.create_index("users")
    await friendships.create_index("pair_key", unique=True)
    await posts.create_index([("author_id", 1), ("created_at", -1)])
    await notifications.create_index([("user_id", 1), ("created_at", -1)])
    await notifications.create_index([("user_id", 1), ("is_read", 1), ("created_at", -1)])


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}


@app.get("/")
async def root():
    return {"name": settings.app_name, "docs": "/docs", "health": "/health"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled application exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
