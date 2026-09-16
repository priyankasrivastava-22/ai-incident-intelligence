import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.incident_signal import IncidentSignal

class IncidentSignalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # Create an incident signal.
    def create(self, *, incident_id: uuid.UUID, signal_type: str, signal_time: datetime, score: float | None = None, baseline: float | None = None, current_value: float | None = None, threshold: float | None = None) -> IncidentSignal:
        signal = IncidentSignal(incident_id=incident_id, signal_type=signal_type, signal_time=signal_time, score=score, baseline=baseline, current_value=current_value, threshold=threshold)
        self.db.add(signal)
        self.db.flush()
        return signal

    # Get signals for an incident.
    def get_for_incident(self, incident_id: uuid.UUID) -> list[IncidentSignal]:
        statement = select(IncidentSignal).where(IncidentSignal.incident_id == incident_id).order_by(IncidentSignal.signal_time)
        return list(self.db.scalars(statement).all())