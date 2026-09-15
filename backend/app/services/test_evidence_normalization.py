from datetime import datetime, timezone
import uuid

from backend.app.models.log_event import LogEvent
from backend.app.services.evidence_normalization_service import EvidenceNormalizationService


def test_normalize_log_event() -> None:
    log_event = LogEvent(
        id=uuid.uuid4(),
        log_file_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc),
        service="booking-api",
        environment="production",
        host="booking-01",
        level="ERROR",
        message="Database connection failed build_id=build-123 deployment_id=deploy-456 trace_id=abc123",
        status_code=500,
        trace_id="abc123",
    )

    evidence = EvidenceNormalizationService().normalize_log_event(log_event)

    assert evidence.source == "application_log"
    assert evidence.layer == "application"
    assert evidence.service == "booking-api"
    assert evidence.environment == "production"
    assert evidence.event_type == "http_server_error"
    assert evidence.severity == "error"
    assert evidence.status == "500"
    assert evidence.trace_id == "abc123"
    assert evidence.build_id == "build-123"
    assert evidence.deployment_id == "deploy-456"


if __name__ == "__main__":
    test_normalize_log_event()
    print("Evidence normalization test passed.")