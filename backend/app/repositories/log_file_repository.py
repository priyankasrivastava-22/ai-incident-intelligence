from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.log_file import LogFile


class LogFileRepository:
    """Provide database operations for ingested log files."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        filename: str,
        file_type: str,
        file_size: int,
        service: str,
        environment: str,
        uploaded_by: UUID,
    ) -> LogFile:
        """Create and persist log-file metadata."""

        log_file = LogFile(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            service=service,
            environment=environment,
            uploaded_by=uploaded_by,
            processing_status="pending",
            total_entries=0,
        )

        self.db.add(log_file)
        self.db.flush()
        self.db.refresh(log_file)

        return log_file

    def get_by_id(self, log_file_id: UUID) -> LogFile | None:
        """Return a log file by primary key."""

        return self.db.scalar(
            select(LogFile).where(LogFile.id == log_file_id)
        )

    def update_processing_status(
        self,
        log_file: LogFile,
        *,
        status: str,
        total_entries: int | None = None,
        error_message: str | None = None,
    ) -> LogFile:
        """Update the processing state of a log file."""

        log_file.processing_status = status

        if total_entries is not None:
            log_file.total_entries = total_entries

        log_file.error_message = error_message

        self.db.flush()
        self.db.refresh(log_file)

        return log_file