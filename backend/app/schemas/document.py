from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.document import DocumentStatus, DocumentFileType

# ------------- Base ---------------
class DocumentBase(BaseModel):
    name: str = Field(..., max_length=255, description="Original file name")
    uploaded_by: Optional[str] = Field(None, max_length=100, description="Uploader identifier")

# ------------- Create --------------
class DocumentCreate(DocumentBase):
    file_path: str = Field(..., description="Path to file on storage")
    file_type: DocumentFileType
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    mime_type: Optional[str] = Field(None, max_length=100)

# ------------- Update --------------
class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[DocumentStatus] = None

# ------------- Response ----------------
class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_type: DocumentFileType
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

# ------------- Paginated list response -------------
class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int = Field(..., description="Total number of documents")
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total_pages: int

# ------------- Upload response ---------------
class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    status: DocumentStatus
    created_at: datetime