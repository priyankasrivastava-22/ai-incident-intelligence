from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.models.log_file import LogFile
from backend.app.repositories.log_file_repository import LogFileRepository


class IngestionValidationError(Exception):
    """Raised when an uploaded log file fails validation."""


class LogIngestionService:
    """Handle log-file ingestion and processing."""

    ALLOWED_EXTENSIONS = {".log", ".txt"}
    ALLOWED_CONTENT_TYPES = {
        "text/plain",
        "application/octet-stream",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, db: Session) -> None:
        self.db = db
        self.log_file_repository = LogFileRepository(db)

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

        The file is read incrementally rather than loaded completely
        into memory.
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

                total_entries += chunk.count(b"\n")

            if total_size > 0:
                total_entries = max(total_entries, 1)

            log_file.file_size = total_size
            log_file.processing_status = "completed"
            log_file.total_entries = total_entries

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
