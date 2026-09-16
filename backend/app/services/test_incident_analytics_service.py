import uuid
from datetime import datetime, timedelta, timezone
from backend.app.core.database import SessionLocal
from backend.app.models.incident import Incident
from backend.app.models.incident_evidence import IncidentEvidence
from backend.app.models.normalized_evidence import NormalizedEvidence
from backend.app.repositories.incident_signal_repository import IncidentSignalRepository
from backend.app.services.incident_analytics_service import IncidentAnalyticsService

def test_incident_analytics_service():
    db = SessionLocal()
    try:
        base_time = datetime.now(timezone.utc)
        incident = Incident(
            incident_key=f"ANALYTICS-{uuid.uuid4().hex[:8]}",
            title="Analytics test incident",
            severity="critical",
            status="open",
            service="payment-service",
            environment="production",
            start_time=base_time,
        )
        evidence = [
            NormalizedEvidence(timestamp=base_time, source="application_log", layer="application", service="payment-service", environment="production", event_type="http_server_error", severity="error", message="HTTP 500", status="500"),
            NormalizedEvidence(timestamp=base_time + timedelta(seconds=1), source="database_log", layer="database", service="payment-service", environment="production", event_type="timeout", severity="critical", message="Database timeout"),
            NormalizedEvidence(timestamp=base_time + timedelta(seconds=2), source="application_log", layer="application", service="payment-service", environment="production", event_type="http_client_error", severity="warning", message="HTTP 404", status="404"),
        ]
        db.add(incident)
        db.add_all(evidence)
        db.flush()
        db.add_all([IncidentEvidence(incident_id=incident.id, normalized_evidence_id=e.id) for e in evidence])
        db.commit()
        service = IncidentAnalyticsService(db)
        summary = service.get_summary(incident.id)
        assert summary["total_events"] == 3
        assert summary["error_count"] == 1
        assert summary["critical_count"] == 1
        assert summary["warning_count"] == 1
        assert summary["http_4xx_count"] == 1
        assert summary["http_5xx_count"] == 1
        assert summary["timeout_count"] == 1
        assert service.get_layer_counts(incident.id) == {"application": 2, "database": 1}
        assert service.get_event_type_counts(incident.id) == {"http_client_error": 1, "http_server_error": 1, "timeout": 1}
    finally:
        db.rollback()
        db.close()


def test_incident_time_signals():
    db = SessionLocal()
    try:
        base_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        incident = Incident(
            incident_key=f"SIGNAL-{uuid.uuid4().hex[:8]}",
            title="Time signal test",
            severity="critical",
            status="open",
            service="payment-service",
            environment="production",
            start_time=base_time,
        )
        evidence = [
            NormalizedEvidence(timestamp=base_time, source="application_log", layer="application", service="payment-service", environment="production", event_type="http_server_error", severity="error", message="HTTP 500", status="500"),
            NormalizedEvidence(timestamp=base_time + timedelta(seconds=10), source="application_log", layer="application", service="payment-service", environment="production", event_type="http_server_error", severity="error", message="HTTP 500", status="500"),
            NormalizedEvidence(timestamp=base_time + timedelta(minutes=1), source="database_log", layer="database", service="payment-service", environment="production", event_type="timeout", severity="critical", message="Database timeout"),
        ]
        db.add(incident)
        db.add_all(evidence)
        db.flush()
        db.add_all([IncidentEvidence(incident_id=incident.id, normalized_evidence_id=e.id) for e in evidence])
        db.commit()
        service = IncidentAnalyticsService(db)
        signals = service.get_time_signals(incident.id)
        values = list(signals.values())
        assert len(values) == 2
        assert values[0]["total_events"] == 2
        assert values[0]["errors"] == 2
        assert values[0]["http_5xx"] == 2
        assert values[1]["total_events"] == 1
        assert values[1]["critical"] == 1
        assert values[1]["timeouts"] == 1
    finally:
        db.rollback()
        db.close()


def test_detect_5xx_anomaly():
    db = SessionLocal()
    try:
        base_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        incident = Incident(
            incident_key=f"ANOMALY-{uuid.uuid4().hex[:8]}",
            title="5xx spike",
            severity="critical",
            status="open",
            service="payment-service",
            environment="production",
            start_time=base_time,
        )
        evidence = []
        for index, count in enumerate([2, 3, 2, 3, 15]):
            for item in range(count):
                evidence.append(
                    NormalizedEvidence(
                        timestamp=base_time + timedelta(minutes=index, seconds=item),
                        source="application_log",
                        layer="application",
                        service="payment-service",
                        environment="production",
                        event_type="http_server_error",
                        severity="error",
                        message="HTTP 500",
                        status="500",
                    )
                )
        db.add(incident)
        db.add_all(evidence)
        db.flush()
        db.add_all([IncidentEvidence(incident_id=incident.id, normalized_evidence_id=e.id) for e in evidence])
        db.commit()
        service = IncidentAnalyticsService(db)
        result = service.detect_5xx_anomaly(incident.id)
        assert result["is_anomaly"] is True
        assert result["current"] == 15
        assert result["baseline"] == 2.5
        assert result["signal_count"] == 5
        signals = IncidentSignalRepository(db).get_for_incident(incident.id)
        assert len(signals) == 1
        assert signals[0].signal_type == "http_5xx_anomaly"
        assert signals[0].current_value == 15
        assert signals[0].baseline == 2.5
        assert signals[0].threshold == 2.0
    finally:
        db.rollback()
        db.close()