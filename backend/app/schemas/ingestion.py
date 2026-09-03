from uuid import UUID

from pydantic import BaseModel, Field


class UploadLogResponse(BaseModel):
    """Response returned after a log file is accepted for ingestion."""

    id: UUID
    filename: str
    file_type: str
    file_size: int
    service: str
    environment: str
    processing_status: str
    total_entries: int


class ManualLogRequest(BaseModel):
    """Validate manually submitted log text."""

    service: str = Field(min_length=1, max_length=100)
    environment: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)


class ManualLogResponse(BaseModel):
    """Response returned after manual log ingestion."""

    id: UUID
    service: str
    environment: str
    processing_status: str
    total_entries: int