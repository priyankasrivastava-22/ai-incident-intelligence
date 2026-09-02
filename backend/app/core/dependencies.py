from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.jwt import decode_access_token
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.revoked_token_repository import RevokedTokenRepository


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Return the authenticated user from a valid JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        jti = payload["jti"]

        if RevokedTokenRepository(db).is_revoked(jti):
            raise credentials_exception

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = UserRepository(db).get_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user


def require_role(required_role: str):
    """Require the authenticated user to have a specific role."""

    def role_checker(
        current_user=Depends(get_current_user),
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return role_checker


def require_admin(
    current_user=Depends(get_current_user),
):
    """Require the authenticated user to have the admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user