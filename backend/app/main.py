from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, feed, friends, ws

app = FastAPI(title="Social Media API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(feed.router, prefix="/feed", tags=["feed"])
app.include_router(friends.router, prefix="/friends", tags=["friends"])
app.include_router(ws.router, prefix="/ws", tags=["ws"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
