from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from app.core.logging import get_logger
from app.models.document import DocumentStatus
from app.models.ocr_result import OcrResult
from app.schemas.ocr_result import OcrResultResponse, OcrStatusResponse
from app.services import document_service, ocr_result_service
from app.tasks.ocr_tasks import run_ocr

logger = get_logger(__name__)
router = APIRouter()


@router.post("/process/{document_id}", response_model=OcrStatusResponse)
def trigger_ocr(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Enqueue OCR task for a document. Processed asynchronously via Celery."""
    doc = document_service.get_document(db, document_id)

    run_ocr.apply_async(
        args=[str(document_id)],
        queue="ocr",
        task_id=f"ocr-{document_id}",
    )

    return OcrStatusResponse(
        document_id=doc.id,
        status=DocumentStatus.PROCESSING,
    )


@router.get("/result/{document_id}", response_model=OcrResultResponse)
def get_ocr_result(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Return the full OCR result (Markdown output) for a document."""
    return ocr_result_service.get_ocr_result(db, document_id)


@router.get("/status/{document_id}", response_model=OcrStatusResponse)
def get_ocr_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Return the current processing status of a document."""
    doc = document_service.get_document(db, document_id)
    result = db.query(OcrResult).filter_by(document_id=document_id).first()

    return OcrStatusResponse(
        document_id=doc.id,
        status=doc.status,
        processing_time=result.processing_time if result else None,
        error_message=result.error_message if result else None,
    )