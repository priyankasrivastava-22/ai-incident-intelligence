from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from backend.app.core.config import settings


def create_access_token(user_id: UUID, role: str) -> tuple[str, int]:
    """Create a signed JWT access token for an authenticated user."""

    expires_in = settings.access_token_expire_minutes * 60
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    payload = {
        "sub": str(user_id),
        "role": role,
        "jti": str(uuid4()),
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_in


def decode_access_token(token: str) -> dict:
    """Decode and validate a signed JWT access token."""

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )