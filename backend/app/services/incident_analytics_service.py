from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from backend.app.models.incident_evidence import IncidentEvidence
from backend.app.models.normalized_evidence import NormalizedEvidence
from backend.app.services.anomaly_detection_service import AnomalyDetectionService
from backend.app.repositories.incident_signal_repository import IncidentSignalRepository

class IncidentAnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.anomaly_service = AnomalyDetectionService()
        self.signal_repository = IncidentSignalRepository(db)

    # Return basic incident event counts.
    def get_summary(self, incident_id, *, start_time: datetime | None = None, end_time: datetime | None = None):
        statement = select(NormalizedEvidence).join(IncidentEvidence, IncidentEvidence.normalized_evidence_id == NormalizedEvidence.id).where(IncidentEvidence.incident_id == incident_id)
        if start_time:
            statement = statement.where(NormalizedEvidence.timestamp >= start_time)
        if end_time:
            statement = statement.where(NormalizedEvidence.timestamp <= end_time)
        events = list(self.db.scalars(statement).all())
        return {
            "total_events": len(events),
            "critical_count": sum(e.severity == "critical" for e in events),
            "error_count": sum(e.severity == "error" for e in events),
            "warning_count": sum(e.severity == "warning" for e in events),
            "http_4xx_count": sum(e.status is not None and 400 <= int(e.status) < 500 for e in events),
            "http_5xx_count": sum(e.status is not None and 500 <= int(e.status) < 600 for e in events),
            "timeout_count": sum(e.event_type == "timeout" for e in events),
        }

    # Count incident evidence by layer.
    def get_layer_counts(self, incident_id):
        statement = select(NormalizedEvidence.layer, func.count(NormalizedEvidence.id)).join(IncidentEvidence, IncidentEvidence.normalized_evidence_id == NormalizedEvidence.id).where(IncidentEvidence.incident_id == incident_id).group_by(NormalizedEvidence.layer).order_by(NormalizedEvidence.layer)
        return {layer: count for layer, count in self.db.execute(statement).all()}

    # Count incident evidence by event type.
    def get_event_type_counts(self, incident_id):
        statement = select(NormalizedEvidence.event_type, func.count(NormalizedEvidence.id)).join(IncidentEvidence, IncidentEvidence.normalized_evidence_id == NormalizedEvidence.id).where(IncidentEvidence.incident_id == incident_id).group_by(NormalizedEvidence.event_type).order_by(NormalizedEvidence.event_type)
        return {event_type: count for event_type, count in self.db.execute(statement).all()}

    # Return event counts grouped into fixed time buckets.
    def get_time_signals(self, incident_id, *, start_time: datetime | None = None, end_time: datetime | None = None, bucket_minutes: int = 1):
        statement = select(NormalizedEvidence).join(IncidentEvidence, IncidentEvidence.normalized_evidence_id == NormalizedEvidence.id).where(IncidentEvidence.incident_id == incident_id)
        if start_time:
            statement = statement.where(NormalizedEvidence.timestamp >= start_time)
        if end_time:
            statement = statement.where(NormalizedEvidence.timestamp <= end_time)
        events = list(self.db.scalars(statement).all())
        buckets = {}
        bucket_seconds = bucket_minutes * 60
        for event in events:
            timestamp = event.timestamp
            epoch = timestamp.timestamp()
            bucket_epoch = epoch - (epoch % bucket_seconds)
            bucket_time = datetime.fromtimestamp(bucket_epoch, tz=timestamp.tzinfo)
            key = bucket_time.isoformat()
            if key not in buckets:
                buckets[key] = {"total_events": 0, "errors": 0, "warnings": 0, "critical": 0, "http_5xx": 0, "timeouts": 0}
            buckets[key]["total_events"] += 1
            buckets[key]["errors"] += event.severity == "error"
            buckets[key]["warnings"] += event.severity == "warning"
            buckets[key]["critical"] += event.severity == "critical"
            buckets[key]["http_5xx"] += event.status is not None and 500 <= int(event.status) < 600
            buckets[key]["timeouts"] += event.event_type == "timeout"
        return dict(sorted(buckets.items()))

    # Detect and persist a 5xx anomaly.
    def detect_5xx_anomaly(self, incident_id, *, start_time: datetime | None = None, end_time: datetime | None = None,
                           threshold: float = 2.0):
        signals = self.get_time_signals(incident_id, start_time=start_time, end_time=end_time)
        error_counts = [signal["http_5xx"] for signal in signals.values()]
        result = self.anomaly_service.detect_error_rate_anomaly(error_counts, threshold)
        result["signal_count"] = len(error_counts)
        if result["is_anomaly"] and signals:
            signal_time = list(signals.keys())[-1]
            self.signal_repository.create(incident_id=incident_id, signal_type="http_5xx_anomaly",
                                          signal_time=datetime.fromisoformat(signal_time), score=result["score"],
                                          baseline=result["baseline"], current_value=result["current"],
                                          threshold=threshold)
            self.db.commit()
        return result