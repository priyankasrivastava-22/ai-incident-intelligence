import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.incident import Incident


class IncidentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # Create an incident.
    def create(self, **kwargs) -> Incident:
        incident = Incident(**kwargs)
        self.db.add(incident)
        self.db.flush()
        return incident

    # Get an incident by ID.
    def get_by_id(self, incident_id: uuid.UUID) -> Incident | None:
        return self.db.scalar(
            select(Incident).where(Incident.id == incident_id)
        )

    # Get an incident by incident key.
    def get_by_key(self, incident_key: str) -> Incident | None:
        return self.db.scalar(
            select(Incident).where(Incident.incident_key == incident_key)
        )

    # Update an incident.
    def update(self, incident: Incident, **kwargs) -> Incident:
        for field, value in kwargs.items():
            setattr(incident, field, value)
        self.db.flush()
        return incident