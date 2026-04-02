from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import validate_upload_file
from app.core.exceptions import DocumentNotFoundException
from db.session import get_db
from app.schemas.document import (
    DocumentResponse,
    DocumentUpdate,
    DocumentUploadResponse,
    DocumentListResponse,
)
from app.services import document_service

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return a paginated list of all documents."""
    return document_service.list_documents(db, page=page, page_size=page_size)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Return details of a single document."""
    return document_service.get_document(db, document_id)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: UploadFile = Depends(validate_upload_file),
):
    """Upload a new document (image or PDF). Returns the created document."""
    contents = await file.read()
    doc = document_service.create_document(db, file, contents)
    return doc


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
):
    """Update document metadata (name, status)."""
    return document_service.update_document(db, document_id, data)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Delete a document and its OCR result."""
    return document_service.delete_document(db, document_id)