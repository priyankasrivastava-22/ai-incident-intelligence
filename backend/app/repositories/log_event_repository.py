import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.log_event import LogEvent


class LogEventRepository:
    """Provide database operations for structured log events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        log_file_id: uuid.UUID,
        timestamp,
        service: str,
        environment: str,
        level: str,
        message: str,
        host: str | None = None,
        endpoint: str | None = None,
        method: str | None = None,
        status_code: int | None = None,
        response_time: float | None = None,
        exception: str | None = None,
        trace_id: str | None = None,
    ) -> LogEvent:
        """Create and stage a single structured log event."""

        log_event = LogEvent(
            log_file_id=log_file_id,
            timestamp=timestamp,
            service=service,
            environment=environment,
            host=host,
            level=level,
            message=message,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            exception=exception,
            trace_id=trace_id,
        )

        self.db.add(log_event)

        return log_event

    def create_many(
        self,
        events: list[LogEvent],
    ) -> None:
        """Stage multiple log events for insertion."""

        if events:
            self.db.add_all(events)

    def get_by_id(
        self,
        log_event_id: uuid.UUID,
    ) -> LogEvent | None:
        """Return a log event by its primary key."""

        return self.db.scalar(
            select(LogEvent).where(LogEvent.id == log_event_id)
        )

    def get_by_log_file_id(
        self,
        log_file_id: uuid.UUID,
    ) -> list[LogEvent]:
        """Return all events belonging to a log file."""

        return list(
            self.db.scalars(
                select(LogEvent)
                .where(LogEvent.log_file_id == log_file_id)
                .order_by(LogEvent.timestamp.asc())
            ).all()
        )