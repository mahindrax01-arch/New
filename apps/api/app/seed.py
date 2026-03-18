from datetime import UTC, datetime

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Conversation, ConversationMember, Message, User

DEMO_USERS = [
    {'email': 'alice@example.com', 'username': 'alice', 'name': 'Alice Park'},
    {'email': 'bob@example.com', 'username': 'bob', 'name': 'Bob Stone'},
    {'email': 'carol@example.com', 'username': 'carol', 'name': 'Carol Diaz'},
]


def main() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(User.id).limit(1)):
            return
        users = []
        for item in DEMO_USERS:
            user = User(**item, password_hash=hash_password('Password123!'), last_seen_at=datetime.now(UTC), bio='Demo account for local development.')
            db.add(user)
            users.append(user)
        db.flush()
        dm = Conversation(title='Alice + Bob', kind='direct', created_by_id=users[0].id, is_secret=False)
        secret_dm = Conversation(title='Secret Inbox', kind='direct', created_by_id=users[0].id, is_secret=True)
        group = Conversation(title='Launch Team', kind='group', description='Product launch coordination', created_by_id=users[0].id, is_secret=False)
        db.add_all([dm, secret_dm, group])
        db.flush()
        for convo, members in [(dm, users[:2]), (secret_dm, users[:2]), (group, users)]:
            for index, member in enumerate(members):
                db.add(ConversationMember(conversation_id=convo.id, user_id=member.id, role='owner' if index == 0 else 'member'))
        db.add_all([
            Message(conversation_id=dm.id, sender_id=users[0].id, body='Hey Bob — the premium chat shell is ready.', plaintext_fallback='Hey Bob — the premium chat shell is ready.'),
            Message(conversation_id=dm.id, sender_id=users[1].id, body='Looks sharp. I am testing reactions and typing now.', plaintext_fallback='Looks sharp. I am testing reactions and typing now.'),
            Message(conversation_id=group.id, sender_id=users[2].id, body='Launch checklist updated. Design QA passed.', plaintext_fallback='Launch checklist updated. Design QA passed.'),
            Message(conversation_id=secret_dm.id, sender_id=users[0].id, body='{"ciphertext":"demo","iv":"demo"}', plaintext_fallback='Encrypted demo message'),
        ])
        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    main()
