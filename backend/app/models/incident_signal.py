import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base

class IncidentSignal(Base):
    __tablename__ = "incident_signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    signal_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    baseline: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), server_default=func.now(), index=True)