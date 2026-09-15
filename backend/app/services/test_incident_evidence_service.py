import uuid
from datetime import datetime, timedelta, timezone
from backend.app.core.database import SessionLocal
from backend.app.models.incident import Incident
from backend.app.models.normalized_evidence import NormalizedEvidence
from backend.app.services.incident_evidence_service import IncidentEvidenceService

def test_incident_evidence_end_to_end():
    db = SessionLocal()
    try:
        base_time = datetime.now(timezone.utc)
        incident = Incident(
            incident_key=f"TEST-{uuid.uuid4().hex[:8]}",
            title="Payment service cascading failure",
            description="Deployment caused application errors followed by database timeouts.",
            severity="critical",
            status="open",
            service="payment-service",
            environment="production",
            start_time=base_time,
        )
        evidence = [
            NormalizedEvidence(
                timestamp=base_time,
                source="ci_cd",
                layer="deployment",
                service="payment-service",
                environment="production",
                event_type="deployment",
                severity="info",
                message="Deployment deployment_id=deploy-1042 build_id=build-782 completed.",
                deployment_id="deploy-1042",
                build_id="build-782",
            ),
            NormalizedEvidence(
                timestamp=base_time + timedelta(seconds=10),
                source="application_log",
                layer="application",
                service="payment-service",
                environment="production",
                event_type="http_server_error",
                severity="error",
                message="HTTP 500 returned by /payments.",
                status="500",
                deployment_id="deploy-1042",
                build_id="build-782",
            ),
            NormalizedEvidence(
                timestamp=base_time + timedelta(seconds=20),
                source="database_log",
                layer="database",
                service="payment-service",
                environment="production",
                event_type="timeout",
                severity="critical",
                message="Database connection timeout.",
                deployment_id="deploy-1042",
            ),
            NormalizedEvidence(
                timestamp=base_time + timedelta(seconds=30),
                source="infrastructure_log",
                layer="infrastructure",
                service="payment-service",
                environment="production",
                event_type="http_server_error",
                severity="error",
                message="Payment requests failing across application hosts.",
                deployment_id="deploy-1042",
            ),
        ]
        db.add(incident)
        db.add_all(evidence)
        db.flush()
        service = IncidentEvidenceService(db)
        for item in evidence:
            service.attach_evidence(incident_id=incident.id, normalized_evidence_id=item.id)
        db.commit()
        linked = service.get_incident_evidence(incident.id)
        assert len(linked) == 4
        assert [item.layer for item in linked] == ["deployment", "application", "database", "infrastructure"]
        assert linked[0].deployment_id == "deploy-1042"
        assert linked[1].status == "500"
        filtered = service.get_incident_evidence(incident.id, layer="database")
        assert len(filtered) == 1
        assert filtered[0].event_type == "timeout"
    finally:
        db.rollback()
        db.close()