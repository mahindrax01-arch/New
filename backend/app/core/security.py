import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv

load_dotenv()
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"


def make_token(subject: str, expires_minutes: int, token_type: str, role: str | None = None) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(UTC) + timedelta(minutes=expires_minutes),
    }
    if role:
        payload["role"] = role
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
