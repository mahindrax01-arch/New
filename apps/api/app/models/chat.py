from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Conversation(Base):
    __tablename__ = 'conversations'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    kind: Mapped[str] = mapped_column(String(16), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    pinned_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    members = relationship('ConversationMember', back_populates='conversation', cascade='all, delete-orphan')
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')


class ConversationMember(Base):
    __tablename__ = 'conversation_members'
    __table_args__ = (UniqueConstraint('conversation_id', 'user_id', name='uq_conversation_user'),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id', ondelete='CASCADE'), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    role: Mapped[str] = mapped_column(String(16), default='member')
    muted: Mapped[bool] = mapped_column(Boolean, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    unread_count: Mapped[int] = mapped_column(Integer, default=0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_read_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    conversation = relationship('Conversation', back_populates='members')
    user = relationship('User', back_populates='memberships')


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id', ondelete='CASCADE'), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    body: Mapped[str] = mapped_column(Text)
    plaintext_fallback: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind: Mapped[str] = mapped_column(String(24), default='text')
    reply_to_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client_nonce: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    conversation = relationship('Conversation', back_populates='messages')
    sender = relationship('User', back_populates='messages')
    delivery_states = relationship('DeliveryState', back_populates='message', cascade='all, delete-orphan')
    reactions = relationship('Reaction', back_populates='message', cascade='all, delete-orphan')
    attachments = relationship('Attachment', back_populates='message', cascade='all, delete-orphan')
    secret_keys = relationship('SecretMessageKey', back_populates='message', cascade='all, delete-orphan')


class DeliveryState(Base):
    __tablename__ = 'delivery_states'
    __table_args__ = (UniqueConstraint('message_id', 'user_id', name='uq_message_delivery_user'),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(16), default='sent')
    seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    message = relationship('Message', back_populates='delivery_states')


class Reaction(Base):
    __tablename__ = 'reactions'
    __table_args__ = (UniqueConstraint('message_id', 'user_id', 'emoji', name='uq_message_reaction'),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    emoji: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    message = relationship('Message', back_populates='reactions')


class Attachment(Base):
    __tablename__ = 'attachments'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'), index=True)
    url: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(Integer)
    original_name: Mapped[str] = mapped_column(String(255))

    message = relationship('Message', back_populates='attachments')


class SecretMessageKey(Base):
    __tablename__ = 'secret_message_keys'
    __table_args__ = (UniqueConstraint('message_id', 'recipient_id', name='uq_message_secret_recipient'),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'), index=True)
    recipient_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    wrapped_key: Mapped[str] = mapped_column(Text)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    algorithm: Mapped[str] = mapped_column(String(64), default='RSA-OAEP/AES-GCM')

    message = relationship('Message', back_populates='secret_keys')


class Block(Base):
    __tablename__ = 'blocks'
    __table_args__ = (UniqueConstraint('blocker_id', 'blocked_id', name='uq_block_pair'),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    blocker_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    blocked_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NotificationPreference(Base):
    __tablename__ = 'notification_preferences'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    desktop_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
