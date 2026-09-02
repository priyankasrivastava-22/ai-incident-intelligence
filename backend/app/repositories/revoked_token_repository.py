from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.models.revoked_token import RevokedToken


class RevokedTokenRepository:
    """Provide database operations for revoked JWTs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def revoke(self, jti: str, expires_at: datetime) -> None:
        """Store a JWT identifier until the token naturally expires."""

        revoked_token = RevokedToken(
            jti=jti,
            expires_at=expires_at,
        )

        self.db.add(revoked_token)
        self.db.flush()

    def is_revoked(self, jti: str) -> bool:
        """Return True if the JWT identifier has been revoked."""

        return self.db.scalar(
            select(RevokedToken.id)
            .where(RevokedToken.jti == jti)
        ) is not None

    def delete_expired(self) -> int:
        """Remove revoked tokens that have already expired."""

        result = self.db.execute(
            delete(RevokedToken).where(
                RevokedToken.expires_at < datetime.now(timezone.utc)
            )
        )

        return result.rowcount or 0
