from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentResponse
from app.services import document_service

router = APIRouter()

@router.get("", response_model=list[DocumentResponse])
def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
):
    """Full-text search across all OCR-processed documents."""
    return document_service.search_documents(db, q)