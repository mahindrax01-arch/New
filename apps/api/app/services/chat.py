from collections import defaultdict
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Conversation, ConversationMember, DeliveryState, Message, Reaction, SecretMessageKey, User
from app.schemas.chat import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse, SecretKeyPayload, UserSummary


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _member_users(self, conversation: Conversation) -> list[UserSummary]:
        return [UserSummary.model_validate(member.user, from_attributes=True) for member in conversation.members]

    def _message_response(self, message: Message) -> MessageResponse:
        reactions = defaultdict(int)
        for reaction in message.reactions:
            reactions[reaction.emoji] += 1
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender=UserSummary.model_validate(message.sender, from_attributes=True),
            body=message.body,
            plaintext_fallback=message.plaintext_fallback,
            kind=message.kind,
            reply_to_message_id=message.reply_to_message_id,
            created_at=message.created_at,
            edited_at=message.edited_at,
            reactions=dict(reactions),
            secret_keys=[
                SecretKeyPayload(recipient_id=key.recipient_id, wrapped_key=key.wrapped_key, signature=key.signature)
                for key in message.secret_keys
            ],
        )

    def list_conversations(self, user: User) -> list[ConversationResponse]:
        stmt = (
            select(Conversation)
            .join(ConversationMember)
            .where(ConversationMember.user_id == user.id)
            .options(
                joinedload(Conversation.members).joinedload(ConversationMember.user),
                joinedload(Conversation.messages).joinedload(Message.sender),
            )
            .order_by(Conversation.updated_at.desc())
        )
        conversations = self.db.scalars(stmt).unique().all()
        items = []
        for conversation in conversations:
            member = next(m for m in conversation.members if m.user_id == user.id)
            last_message = sorted(conversation.messages, key=lambda m: m.created_at or datetime.min.replace(tzinfo=UTC))[-1] if conversation.messages else None
            items.append(
                ConversationResponse(
                    id=conversation.id,
                    title=conversation.title,
                    kind=conversation.kind,
                    description=conversation.description,
                    is_secret=conversation.is_secret,
                    avatar_url=conversation.avatar_url,
                    members=self._member_users(conversation),
                    last_message=self._message_response(last_message) if last_message else None,
                    unread_count=member.unread_count,
                )
            )
        return items

    def create_conversation(self, user: User, payload: ConversationCreate) -> ConversationResponse:
        if payload.kind == 'direct' and len(payload.member_ids) != 1:
            raise HTTPException(status_code=400, detail='Direct chats require exactly one target member')
        member_ids = list(dict.fromkeys([user.id, *payload.member_ids]))
        members = list(self.db.scalars(select(User).where(User.id.in_(member_ids))).all())
        if len(members) != len(member_ids):
            raise HTTPException(status_code=404, detail='A requested member does not exist')
        conversation = Conversation(
            title=payload.title,
            description=payload.description,
            kind=payload.kind,
            is_secret=payload.is_secret,
            created_by_id=user.id,
        )
        self.db.add(conversation)
        self.db.flush()
        for member in members:
            role = 'owner' if member.id == user.id else 'member'
            self.db.add(ConversationMember(conversation_id=conversation.id, user_id=member.id, role=role))
        self.db.commit()
        return self.get_conversation(user, conversation.id)

    def get_conversation(self, user: User, conversation_id: str) -> ConversationResponse:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .join(ConversationMember)
            .where(ConversationMember.user_id == user.id)
            .options(
                joinedload(Conversation.members).joinedload(ConversationMember.user),
                joinedload(Conversation.messages).joinedload(Message.sender),
                joinedload(Conversation.messages).joinedload(Message.reactions),
                joinedload(Conversation.messages).joinedload(Message.secret_keys),
            )
        )
        conversation = self.db.scalar(stmt)
        if not conversation:
            raise HTTPException(status_code=404, detail='Conversation not found')
        last_message = max(conversation.messages, key=lambda msg: msg.created_at, default=None)
        member = next(m for m in conversation.members if m.user_id == user.id)
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            kind=conversation.kind,
            description=conversation.description,
            is_secret=conversation.is_secret,
            avatar_url=conversation.avatar_url,
            members=self._member_users(conversation),
            last_message=self._message_response(last_message) if last_message else None,
            unread_count=member.unread_count,
        )

    def list_messages(self, user: User, conversation_id: str) -> list[MessageResponse]:
        self.get_conversation(user, conversation_id)
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .options(joinedload(Message.sender), joinedload(Message.reactions), joinedload(Message.secret_keys))
            .order_by(Message.created_at.asc())
            .limit(100)
        )
        return [self._message_response(message) for message in self.db.scalars(stmt).unique().all()]

    def create_message(self, user: User, payload: MessageCreate) -> MessageResponse:
        conversation = self.db.scalar(
            select(Conversation)
            .where(Conversation.id == payload.conversation_id)
            .join(ConversationMember)
            .where(ConversationMember.user_id == user.id)
            .options(joinedload(Conversation.members))
        )
        if not conversation:
            raise HTTPException(status_code=404, detail='Conversation not found')
        if payload.client_nonce:
            duplicate = self.db.scalar(select(Message).where(Message.client_nonce == payload.client_nonce))
            if duplicate:
                return self._message_response(duplicate)
        message = Message(
            conversation_id=payload.conversation_id,
            sender_id=user.id,
            body=payload.body,
            plaintext_fallback=payload.plaintext_fallback,
            kind=payload.kind,
            reply_to_message_id=payload.reply_to_message_id,
            client_nonce=payload.client_nonce,
        )
        self.db.add(message)
        self.db.flush()
        for member in conversation.members:
            status_value = 'seen' if member.user_id == user.id else 'delivered'
            self.db.add(DeliveryState(message_id=message.id, user_id=member.user_id, status=status_value))
            if member.user_id != user.id:
                member.unread_count += 1
        for item in payload.secret_keys:
            self.db.add(SecretMessageKey(message_id=message.id, recipient_id=item.recipient_id, wrapped_key=item.wrapped_key, signature=item.signature))
        conversation.updated_at = datetime.now(UTC)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(message)
        statement = select(Message).where(Message.id == message.id).options(joinedload(Message.sender), joinedload(Message.reactions), joinedload(Message.secret_keys))
        return self._message_response(self.db.scalar(statement))

    def add_reaction(self, user: User, message_id: str, emoji: str) -> MessageResponse:
        message = self.db.scalar(select(Message).where(Message.id == message_id).options(joinedload(Message.sender), joinedload(Message.reactions), joinedload(Message.secret_keys)))
        if not message:
            raise HTTPException(status_code=404, detail='Message not found')
        if not self.db.scalar(select(func.count()).select_from(ConversationMember).where(ConversationMember.conversation_id == message.conversation_id, ConversationMember.user_id == user.id)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a member of the conversation')
        exists = self.db.scalar(select(Reaction).where(Reaction.message_id == message_id, Reaction.user_id == user.id, Reaction.emoji == emoji))
        if not exists:
            self.db.add(Reaction(message_id=message_id, user_id=user.id, emoji=emoji))
            self.db.commit()
            message = self.db.scalar(select(Message).where(Message.id == message_id).options(joinedload(Message.sender), joinedload(Message.reactions), joinedload(Message.secret_keys)))
        return self._message_response(message)
