from alembic import op
import sqlalchemy as sa

revision = '20260318_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=40), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('avatar_url', sa.String(length=512)),
        sa.Column('bio', sa.Text()),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('public_key', sa.Text()),
        sa.Column('encrypted_private_key', sa.Text()),
        sa.Column('private_key_salt', sa.String(length=255)),
        sa.Column('notification_preferences', sa.Text(), nullable=False),
        sa.Column('theme', sa.String(length=16), nullable=False),
        sa.Column('is_online', sa.Boolean(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_table('conversations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=120)),
        sa.Column('kind', sa.String(length=16), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('avatar_url', sa.String(length=512)),
        sa.Column('is_secret', sa.Boolean(), nullable=False),
        sa.Column('created_by_id', sa.String(length=36), sa.ForeignKey('users.id')),
        sa.Column('pinned_message_id', sa.String(length=36)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('archived_at', sa.DateTime(timezone=True))
    )
    op.create_index('ix_conversations_kind', 'conversations', ['kind'])
    op.create_table('conversation_members',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='CASCADE')),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('role', sa.String(length=16), nullable=False),
        sa.Column('muted', sa.Boolean(), nullable=False),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('unread_count', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_read_message_id', sa.String(length=36)),
        sa.UniqueConstraint('conversation_id','user_id', name='uq_conversation_user')
    )
    op.create_index('ix_conversation_members_conversation_id', 'conversation_members', ['conversation_id'])
    op.create_index('ix_conversation_members_user_id', 'conversation_members', ['user_id'])
    op.create_table('messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='CASCADE')),
        sa.Column('sender_id', sa.String(length=36), sa.ForeignKey('users.id')),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('plaintext_fallback', sa.Text()),
        sa.Column('kind', sa.String(length=24), nullable=False),
        sa.Column('reply_to_message_id', sa.String(length=36)),
        sa.Column('edited_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('client_nonce', sa.String(length=80), unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_table('delivery_states',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('message_id', sa.String(length=36), sa.ForeignKey('messages.id', ondelete='CASCADE')),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('seen_at', sa.DateTime(timezone=True)),
        sa.Column('delivered_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('message_id','user_id', name='uq_message_delivery_user')
    )
    op.create_index('ix_delivery_states_message_id', 'delivery_states', ['message_id'])
    op.create_index('ix_delivery_states_user_id', 'delivery_states', ['user_id'])
    op.create_table('reactions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('message_id', sa.String(length=36), sa.ForeignKey('messages.id', ondelete='CASCADE')),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('emoji', sa.String(length=16), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('message_id', 'user_id', 'emoji', name='uq_message_reaction')
    )
    op.create_table('attachments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('message_id', sa.String(length=36), sa.ForeignKey('messages.id', ondelete='CASCADE')),
        sa.Column('url', sa.String(length=512), nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
    )
    op.create_table('secret_message_keys',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('message_id', sa.String(length=36), sa.ForeignKey('messages.id', ondelete='CASCADE')),
        sa.Column('recipient_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('wrapped_key', sa.Text(), nullable=False),
        sa.Column('signature', sa.Text()),
        sa.Column('algorithm', sa.String(length=64), nullable=False),
        sa.UniqueConstraint('message_id','recipient_id', name='uq_message_secret_recipient')
    )
    op.create_table('blocks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('blocker_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('blocked_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('blocker_id','blocked_id', name='uq_block_pair')
    )
    op.create_table('notification_preferences',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('email_enabled', sa.Boolean(), nullable=False),
        sa.Column('push_enabled', sa.Boolean(), nullable=False),
        sa.Column('desktop_enabled', sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    for table in ['notification_preferences','blocks','secret_message_keys','attachments','reactions','delivery_states','messages','conversation_members','conversations']:
        op.drop_table(table)
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
