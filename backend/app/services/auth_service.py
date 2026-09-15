from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.core.security import hash_password, verify_password
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    """Raised when authentication credentials are invalid."""


class DuplicateEmailError(Exception):
    """Raised when a registration email already exists."""


class AuthService:
    """Handle authentication business logic."""
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, email: str, password: str) -> User:
        """Register a new user with a securely hashed password."""
        normalized_email = email.strip().lower()
        if self.user_repository.get_by_email(normalized_email):
            raise DuplicateEmailError
        user = self.user_repository.create(
            email=normalized_email,
            password_hash=hash_password(password),
        )
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateEmailError from exc
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user using email and password."""
        normalized_email = email.strip().lower()
        user = self.user_repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError
        return user