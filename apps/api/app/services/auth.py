from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import SessionUser, SignUpRequest, TokenPair


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def signup(self, payload: SignUpRequest) -> SessionUser:
        existing = self.db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')
        user = User(
            email=payload.email,
            username=payload.username,
            name=payload.name,
            password_hash=hash_password(payload.password),
            public_key=payload.public_key,
            encrypted_private_key=payload.encrypted_private_key,
            private_key_salt=payload.private_key_salt,
            last_seen_at=datetime.now(UTC),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return SessionUser.model_validate(user, from_attributes=True)

    def signin(self, email: str, password: str) -> tuple[SessionUser, TokenPair]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        user.is_online = True
        user.last_seen_at = datetime.now(UTC)
        self.db.add(user)
        self.db.commit()
        access = create_token(user.id, 'access', timedelta(minutes=self.settings.access_token_expire_minutes))
        refresh = create_token(user.id, 'refresh', timedelta(minutes=self.settings.refresh_token_expire_minutes))
        return SessionUser.model_validate(user, from_attributes=True), TokenPair(access_token=access, refresh_token=refresh)
