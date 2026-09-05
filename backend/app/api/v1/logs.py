from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.ingestion import (UploadLogResponse, ManualLogRequest, ManualLogResponse,)
from backend.app.services.ingestion_service import (
    IngestionValidationError,
    LogIngestionService,
)


router = APIRouter(
    prefix="/logs",
    tags=["Log Ingestion"],
)


@router.post(
    "/upload",
    response_model=UploadLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_log_file(
    file: UploadFile = File(...),
    service: str = Form(..., min_length=1, max_length=100),
    environment: str = Form(..., min_length=1, max_length=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and process a .log or .txt file."""

    ingestion_service = LogIngestionService(db)

    try:
        log_file = await ingestion_service.ingest_file(
            file=file,
            service=service.strip(),
            environment=environment.strip(),
            uploaded_by=current_user.id,
        )

        return UploadLogResponse.model_validate(log_file)

    except IngestionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()


@router.post(
    "/manual",
    response_model=ManualLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_manual_log(
    payload: ManualLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept and process manually submitted log text."""

    ingestion_service = LogIngestionService(db)

    try:
        log_file = ingestion_service.ingest_manual_log(
            service=payload.service.strip(),
            environment=payload.environment.strip(),
            content=payload.content,
            uploaded_by=current_user.id,
        )

        return ManualLogResponse.model_validate(log_file)

    except IngestionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc