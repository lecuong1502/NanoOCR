from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import OcrResultNotFoundException, DocumentNotFoundException
from app.core.logging import get_logger
from app.models.document import Document, DocumentStatus
from app.models.ocr_result import OcrResult
from app.services.ocr_service import OcrOutput

logger = get_logger(__name__)


def create_or_update_ocr_result(
    db: Session,
    document: Document,
    output: OcrOutput,
) -> OcrResult:
    """Persist OCR output. Replaces existing result if present."""
    existing = db.query(OcrResult).filter(
        OcrResult.document_id == document.id
    ).first()

    if existing:
        result = existing
    else:
        result = OcrResult(document_id=document.id)
        db.add(result)

    result.raw_text = output.raw_text
    result.markdown_output = output.markdown_output
    result.confidence = output.confidence
    result.language = output.language
    result.page_count = output.page_count
    result.model_version = output.model_version
    result.processing_time = output.processing_time
    result.error_message = None

    document.status = DocumentStatus.DONE
    db.commit()
    db.refresh(result)
    logger.info(f"Saved OCR result for document: {document.id}")
    return result


def save_ocr_error(
    db: Session,
    document: Document,
    error_message: str,
) -> None:
    """Mark document as failed and persist error message."""
    document.status = DocumentStatus.FAILED

    existing = db.query(OcrResult).filter(
        OcrResult.document_id == document.id
    ).first()
    if existing:
        existing.error_message = error_message
    else:
        db.add(OcrResult(
            document_id=document.id,
            error_message=error_message,
        ))

    db.commit()
    logger.error(f"OCR failed for document {document.id}: {error_message}")


def get_ocr_result(db: Session, document_id: uuid.UUID) -> OcrResult:
    result = db.query(OcrResult).filter(
        OcrResult.document_id == document_id
    ).first()
    if not result:
        raise OcrResultNotFoundException(str(document_id))
    return result