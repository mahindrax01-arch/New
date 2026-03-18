from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def search(self, query: str, exclude_user_id: str | None = None) -> list[User]:
        stmt = select(User).where((User.name.ilike(f'%{query}%')) | (User.username.ilike(f'%{query}%')))
        if exclude_user_id:
            stmt = stmt.where(User.id != exclude_user_id)
        return list(self.db.scalars(stmt.limit(10)).all())
