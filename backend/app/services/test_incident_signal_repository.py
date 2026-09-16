import uuid
from datetime import datetime, timezone
from backend.app.core.database import SessionLocal
from backend.app.models.incident import Incident
from backend.app.repositories.incident_signal_repository import IncidentSignalRepository

def test_incident_signal_repository():
    db = SessionLocal()
    try:
        incident = Incident(incident_key=f"SIGNAL-{uuid.uuid4().hex[:8]}", title="5xx anomaly", severity="critical", status="open", service="payment-service", environment="production", start_time=datetime.now(timezone.utc))
        db.add(incident)
        db.flush()
        repository = IncidentSignalRepository(db)
        signal = repository.create(incident_id=incident.id, signal_type="http_5xx_anomaly", signal_time=incident.start_time, score=5.0, baseline=2.5, current_value=15, threshold=2.0)
        db.commit()
        signals = repository.get_for_incident(incident.id)
        assert len(signals) == 1
        assert signals[0].signal_type == "http_5xx_anomaly"
        assert signals[0].current_value == 15
    finally:
        db.rollback()
        db.close()