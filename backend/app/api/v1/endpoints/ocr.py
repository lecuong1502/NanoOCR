from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from db.session import get_db
from app.core.logging import get_logger
from app.models.document import DocumentStatus
from app.schemas.ocr_result import OcrResultResponse, OcrStatusResponse
from app.services import document_service, ocr_result_service
from app.services.storage_service import download_file

logger = get_logger(__name__)
router = APIRouter()


def _run_ocr_task(document_id: uuid.UUID) -> None:
    """Background task: download file → run OCR → persist result."""
    from db.session import SessionLocal
    from app.services.ocr_service import process_image, process_pdf

    db = SessionLocal()
    try:
        doc = document_service.get_document(db, document_id)
        doc.status = DocumentStatus.PROCESSING
        db.commit()

        file_bytes = download_file(doc.file_path)

        if doc.file_type.value == "pdf":
            output = process_pdf(file_bytes)
        else:
            output = process_image(file_bytes, mime_type=doc.mime_type or "image/jpeg")

        ocr_result_service.create_or_update_ocr_result(db, doc, output)
        logger.info(f"OCR completed for document {document_id}")
    
    except Exception as exc:
        logger.exception(f"OCR failed for document {document_id}: {exc}")
        try:
            ocr_result_service.save_ocr_error(db, doc, str(exc))
        except Exception:
            pass
    finally:
        db.close()


@router.post("/process/{document_id}", response_model=OcrStatusResponse)
def trigger_ocr(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger OCR processing for a document. Runs in the background."""
    doc = document_service.get_document(db, document_id)
    background_tasks.add_task(_run_ocr_task, document_id)
    return OcrStatusResponse(document_id=doc.id, status=DocumentStatus.PROCESSING)


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
    result = db.query(__import__("app.models.ocr_result", fromlist=["OcrResult"]).OcrResult).filter_by(
        document_id=document_id
    ).first()
    return OcrStatusResponse(
        document_id=doc.id,
        status=doc.status,
        processing_time=result.processing_time if result else None,
        error_message=result.error_message if result else None,
    )