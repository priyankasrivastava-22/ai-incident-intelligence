import uuid
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class IncidentService(Base):
    __tablename__ = "incident_services"

    __table_args__ = (
        UniqueConstraint(
            "incident_id",
            "service",
            name="uq_incident_services_incident_service",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    impact_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )