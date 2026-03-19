from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# Use a pure-Python password hash to avoid local bcrypt backend incompatibilities.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _build_payload(subject: str, token_type: str, expires_delta: timedelta) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "sub": subject,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }


def create_access_token(subject: str) -> dict[str, Any]:
    payload = _build_payload(subject, "access", timedelta(minutes=settings.access_token_expire_minutes))
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return {"token": token, "jti": payload["jti"], "exp": payload["exp"]}


def create_refresh_token(subject: str, family: str | None = None) -> dict[str, Any]:
    payload = _build_payload(subject, "refresh", timedelta(days=settings.refresh_token_expire_days))
    payload["family"] = family or str(uuid4())
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return {
        "token": token,
        "jti": payload["jti"],
        "exp": payload["exp"],
        "family": payload["family"],
    }


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
