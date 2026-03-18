from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user, db_session
from app.core.config import get_settings
from app.core.security import create_token, decode_token
from app.models.user import User
from app.schemas.auth import SessionUser, SignInRequest, SignUpRequest, TokenPair
from app.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=SessionUser)
def signup(payload: SignUpRequest, db: Session = Depends(db_session)) -> SessionUser:
    return AuthService(db).signup(payload)


@router.post('/signin')
def signin(payload: SignInRequest, db: Session = Depends(db_session)) -> dict:
    user, tokens = AuthService(db).signin(payload.email, payload.password)
    return {'user': user.model_dump(), 'tokens': tokens.model_dump()}


@router.post('/refresh', response_model=TokenPair)
def refresh(payload: TokenPair) -> TokenPair:
    settings = get_settings()
    decoded = decode_token(payload.refresh_token)
    return TokenPair(
        access_token=create_token(decoded['sub'], 'access', timedelta(minutes=settings.access_token_expire_minutes)),
        refresh_token=create_token(decoded['sub'], 'refresh', timedelta(minutes=settings.refresh_token_expire_minutes)),
    )


@router.get('/me', response_model=SessionUser)
def me(user: User = Depends(current_user)) -> SessionUser:
    return SessionUser.model_validate(user, from_attributes=True)
