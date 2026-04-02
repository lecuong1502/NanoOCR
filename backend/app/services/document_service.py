from __future__ import annotations

import math
import uuid
from typing import BinaryIO

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import DocumentNotFoundException
from app.core.logging import get_logger
from app.models.document import Document, DocumentStatus, DocumentFileType
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentListResponse, DocumentResponse
from app.services import storage_service

logger = get_logger(__name__)

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/tiff", "image/webp"}
PDF_MIME_TYPE = "application/pdf"


# -------------- CRUD --------------

def create_document(db: Session, file: UploadFile, contents: bytes) -> Document:
    mime = file.content_type or "application/octet-stream"
    file_type = DocumentFileType.PDF if mime == PDF_MIME_TYPE else DocumentFileType.IMAGE

    import io
    object_name = storage_service.upload_file(
        file_data=io.BytesIO(contents),
        filename=file.filename or "upload",
        content_type=mime,
        size=len(contents),
    )

    doc = Document(
        name=file.filename or "upload",
        file_path=object_name,
        file_type=file_type,
        file_size=len(contents),
        mime_type=mime,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info(f"Created document: {doc.id}")
    return doc


def get_document(db: Session, document_id: uuid.UUID) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise DocumentNotFoundException(str(document_id))
    return doc


def list_documents(
    db: Session,
    page: int = 1,
    page_size: int = 20
) -> DocumentListResponse:
    total = db.query(Document).count()
    items = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


def update_document(db: Session, document_id: uuid.UUID, data: DocumentUpdate) -> Document:
    doc = get_document(db, document_id)
    if data.name is not None:
        doc.name = data.name
    if data.status is not None:
        doc.status = data.status
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, document_id: uuid.UUID) -> None:
    doc = get_document(db, document_id)
    # Delete file from storage
    try:
        storage_service.delete_file(doc.file_path)
    except Exception as e:
        logger.warning(f"Could not delete file from storage: {e}")
    db.delete(doc)
    db.commit()
    logger.info(f"Deleted document: {document_id}")


def search_documents(db: Session, query: str) -> list[Document]:
    from app.models.ocr_result import OcrResult
    return (
        db.query(Document)
        .join(OcrResult, Document.id == OcrResult.document_id)
        .filter(OcrResult.markdown_output.ilike(f"%{query}%"))
        .order_by(Document.created_at.desc())
        .all()
    )