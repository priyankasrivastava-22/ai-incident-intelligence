import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.incident_evidence import IncidentEvidence
from backend.app.models.normalized_evidence import NormalizedEvidence

class IncidentEvidenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # Attach normalized evidence to an incident.
    def create(self, *, incident_id: uuid.UUID, normalized_evidence_id: uuid.UUID, relationship_type: str = "supporting") -> IncidentEvidence:
        evidence = IncidentEvidence(incident_id=incident_id, normalized_evidence_id=normalized_evidence_id, relationship_type=relationship_type)
        self.db.add(evidence)
        self.db.flush()
        return evidence

    # Get evidence linked to an incident with investigation filters.
    def get_for_incident(self, incident_id: uuid.UUID, *, start_time: datetime | None = None, end_time: datetime | None = None, service: str | None = None, environment: str | None = None, layer: str | None = None, severity: str | None = None, event_type: str | None = None) -> list[NormalizedEvidence]:
        statement = select(NormalizedEvidence).join(IncidentEvidence, IncidentEvidence.normalized_evidence_id == NormalizedEvidence.id).where(IncidentEvidence.incident_id == incident_id)
        if start_time:
            statement = statement.where(NormalizedEvidence.timestamp >= start_time)
        if end_time:
            statement = statement.where(NormalizedEvidence.timestamp <= end_time)
        if service:
            statement = statement.where(NormalizedEvidence.service == service)
        if environment:
            statement = statement.where(NormalizedEvidence.environment == environment)
        if layer:
            statement = statement.where(NormalizedEvidence.layer == layer)
        if severity:
            statement = statement.where(NormalizedEvidence.severity == severity)
        if event_type:
            statement = statement.where(NormalizedEvidence.event_type == event_type)
        statement = statement.order_by(NormalizedEvidence.timestamp)
        return list(self.db.scalars(statement).all())