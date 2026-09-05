from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.models.log_event import LogEvent
from backend.app.models.log_file import LogFile
from backend.app.ingestion.parser import LogParser
from backend.app.repositories.log_event_repository import LogEventRepository
from backend.app.repositories.log_file_repository import LogFileRepository


class IngestionValidationError(Exception):
    """Raised when an uploaded log file fails validation."""


class LogIngestionService:
    """Handle log-file ingestion, parsing, and persistence."""

    ALLOWED_EXTENSIONS = {".log", ".txt"}

    ALLOWED_CONTENT_TYPES = {
        "text/plain",
        "application/octet-stream",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024

    CHUNK_SIZE = 1024 * 1024

    EVENT_BATCH_SIZE = 500

    MAX_MANUAL_LOG_SIZE = 5 * 1024 * 1024

    def __init__(self, db: Session) -> None:
        self.db = db

        self.log_file_repository = LogFileRepository(db)
        self.log_event_repository = LogEventRepository(db)

        self.parser = LogParser()

    def validate_file(
        self,
        filename: str | None,
        content_type: str | None,
    ) -> str:
        """Validate the uploaded file and return its extension."""

        if not filename:
            raise IngestionValidationError(
                "A filename is required."
            )

        extension = Path(filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise IngestionValidationError(
                "Only .log and .txt files are allowed."
            )

        if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
            raise IngestionValidationError(
                "Unsupported file content type."
            )

        return extension

    def _build_event(
        self,
        *,
        parsed_log,
        log_file_id: UUID,
        service: str,
        environment: str,
    ) -> LogEvent:
        """Convert a parsed log line into a LogEvent model."""

        return LogEvent(
            log_file_id=log_file_id,
            timestamp=parsed_log.timestamp,
            service=service,
            environment=environment,
            host=parsed_log.host,
            level=parsed_log.level,
            message=parsed_log.message,
            endpoint=parsed_log.endpoint,
            method=parsed_log.method,
            status_code=parsed_log.status_code,
            response_time=parsed_log.response_time,
            exception=parsed_log.exception,
            trace_id=parsed_log.trace_id,
        )

    def _process_line(
        self,
        *,
        line: str,
        log_file_id: UUID,
        service: str,
        environment: str,
        events: list[LogEvent],
    ) -> int:
        """Parse one line and append a valid event to the batch."""

        parsed_log = self.parser.parse(line)

        if parsed_log is None:
            return 0

        events.append(
            self._build_event(
                parsed_log=parsed_log,
                log_file_id=log_file_id,
                service=service,
                environment=environment,
            )
        )

        if len(events) >= self.EVENT_BATCH_SIZE:
            self.log_event_repository.create_many(events)
            self.db.flush()
            events.clear()

        return 1

    async def ingest_file(
        self,
        *,
        file: UploadFile,
        service: str,
        environment: str,
        uploaded_by: UUID,
    ) -> LogFile:
        """
        Validate and ingest an uploaded log file.

        The file is read incrementally in chunks and log events
        are persisted in batches.
        """

        extension = self.validate_file(
            file.filename,
            file.content_type,
        )

        total_size = 0
        total_entries = 0

        log_file = self.log_file_repository.create(
            filename=file.filename,
            file_type=extension.lstrip("."),
            file_size=0,
            service=service,
            environment=environment,
            uploaded_by=uploaded_by,
        )

        log_file.processing_status = "processing"
        self.db.flush()

        events: list[LogEvent] = []

        # Bytes left over from the previous chunk because the final
        # line in that chunk may be incomplete.
        buffer = b""

        try:
            while True:
                chunk = await file.read(self.CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > self.MAX_FILE_SIZE:
                    raise IngestionValidationError(
                        "File size exceeds the 10 MB limit."
                    )

                buffer += chunk

                lines = buffer.split(b"\n")

                # Keep the final incomplete line in the buffer.
                buffer = lines.pop()

                for raw_line in lines:
                    line = raw_line.decode(
                        "utf-8",
                        errors="replace",
                    )

                    total_entries += self._process_line(
                        line=line,
                        log_file_id=log_file.id,
                        service=service,
                        environment=environment,
                        events=events,
                    )

            # Process the final line when the file does not end
            # with a newline.
            if buffer:
                line = buffer.decode(
                    "utf-8",
                    errors="replace",
                )

                total_entries += self._process_line(
                    line=line,
                    log_file_id=log_file.id,
                    service=service,
                    environment=environment,
                    events=events,
                )

            # Persist the final partial batch.
            if events:
                self.log_event_repository.create_many(events)
                self.db.flush()
                events.clear()

            log_file.file_size = total_size
            log_file.processing_status = "completed"
            log_file.total_entries = total_entries
            log_file.processed_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(log_file)

            return log_file

        except Exception as exc:
            self.db.rollback()

            if isinstance(exc, IngestionValidationError):
                raise

            raise IngestionValidationError(
                "Log file processing failed."
            ) from exc

    def ingest_manual_log(
        self,
        *,
        service: str,
        environment: str,
        content: str,
        uploaded_by: UUID,
    ) -> LogFile:
        """Ingest manually submitted log text."""

        if not content.strip():
            raise IngestionValidationError(
                "Log content cannot be empty."
            )

        content_size = len(content.encode("utf-8"))

        if content_size > self.MAX_MANUAL_LOG_SIZE:
            raise IngestionValidationError(
                "Manual log content exceeds the 5 MB limit."
            )

        log_file = self.log_file_repository.create(
            filename="manual-input.log",
            file_type="manual",
            file_size=content_size,
            service=service,
            environment=environment,
            uploaded_by=uploaded_by,
        )

        log_file.processing_status = "processing"
        self.db.flush()

        events: list[LogEvent] = []
        total_entries = 0

        try:
            for line in content.splitlines():
                total_entries += self._process_line(
                    line=line,
                    log_file_id=log_file.id,
                    service=service,
                    environment=environment,
                    events=events,
                )

            if events:
                self.log_event_repository.create_many(events)
                self.db.flush()
                events.clear()

            log_file.processing_status = "completed"
            log_file.total_entries = total_entries
            log_file.processed_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(log_file)

            return log_file

        except Exception as exc:
            self.db.rollback()

            if isinstance(exc, IngestionValidationError):
                raise

            raise IngestionValidationError(
                "Manual log processing failed."
            ) from exc