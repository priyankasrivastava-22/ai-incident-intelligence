import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.repositories.incident_repository import IncidentRepository
from backend.app.repositories.incident_evidence_repository import IncidentEvidenceRepository

class IncidentEvidenceService:
    def __init__(self, db: Session) -> None:
        self.incident_repository = IncidentRepository(db)
        self.evidence_repository = IncidentEvidenceRepository(db)

    # Attach evidence to an incident.
    def attach_evidence(self, *, incident_id: uuid.UUID, normalized_evidence_id: uuid.UUID, relationship_type: str = "supporting"):
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise ValueError("Incident not found.")
        return self.evidence_repository.create(incident_id=incident_id, normalized_evidence_id=normalized_evidence_id, relationship_type=relationship_type)

    # Retrieve incident evidence using investigation filters.
    def get_incident_evidence(self, incident_id: uuid.UUID, *, start_time: datetime | None = None, end_time: datetime | None = None, service: str | None = None, environment: str | None = None, layer: str | None = None, severity: str | None = None, event_type: str | None = None):
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise ValueError("Incident not found.")
        return self.evidence_repository.get_for_incident(incident_id, start_time=start_time, end_time=end_time, service=service, environment=environment, layer=layer, severity=severity, event_type=event_type)