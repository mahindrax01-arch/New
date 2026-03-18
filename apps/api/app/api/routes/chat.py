from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user, db_session
from app.models.user import User
from app.schemas.chat import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse, ReactionCreate, UserSummary
from app.services.chat import ChatService
from app.repositories.users import UserRepository

router = APIRouter(prefix='/chat', tags=['chat'])


@router.get('/conversations', response_model=list[ConversationResponse])
def list_conversations(user: User = Depends(current_user), db: Session = Depends(db_session)) -> list[ConversationResponse]:
    return ChatService(db).list_conversations(user)


@router.post('/conversations', response_model=ConversationResponse)
def create_conversation(payload: ConversationCreate, user: User = Depends(current_user), db: Session = Depends(db_session)) -> ConversationResponse:
    return ChatService(db).create_conversation(user, payload)


@router.get('/conversations/{conversation_id}', response_model=ConversationResponse)
def get_conversation(conversation_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)) -> ConversationResponse:
    return ChatService(db).get_conversation(user, conversation_id)


@router.get('/conversations/{conversation_id}/messages', response_model=list[MessageResponse])
def list_messages(conversation_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)) -> list[MessageResponse]:
    return ChatService(db).list_messages(user, conversation_id)


@router.post('/messages', response_model=MessageResponse)
def create_message(payload: MessageCreate, user: User = Depends(current_user), db: Session = Depends(db_session)) -> MessageResponse:
    return ChatService(db).create_message(user, payload)


@router.post('/messages/{message_id}/reactions', response_model=MessageResponse)
def add_reaction(message_id: str, payload: ReactionCreate, user: User = Depends(current_user), db: Session = Depends(db_session)) -> MessageResponse:
    return ChatService(db).add_reaction(user, message_id, payload.emoji)


@router.get('/users/search', response_model=list[UserSummary])
def search_users(q: str, user: User = Depends(current_user), db: Session = Depends(db_session)) -> list[UserSummary]:
    return [UserSummary.model_validate(item, from_attributes=True) for item in UserRepository(db).search(q, exclude_user_id=user.id)]
