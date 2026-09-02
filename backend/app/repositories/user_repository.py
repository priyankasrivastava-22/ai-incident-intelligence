from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.user import User


class UserRepository:
    """Provide database operations for users."""
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by primary key."""
        return self.db.scalar(
            select(User).where(User.id == user_id)
        )

    def get_by_email(self, email: str) -> User | None:
        """Return a user by normalized email address."""
        return self.db.scalar(
            select(User).where(User.email == email)
        )

    def create(self, email: str, password_hash: str) -> User:
        """Create and persist a new user."""
        user = User(
            email=email,
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)

        return user