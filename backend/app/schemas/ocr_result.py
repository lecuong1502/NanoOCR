from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.document import DocumentStatus

# ------------ Response (full OCR result) -------------
class OcrResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID

    raw_text: Optional[str] = None
    markdown_output: Optional[str] = None

    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Overall confidence score (0.0 – 1.0)"
    )
    language: Optional[str] = Field(None, description="Detected language code, e.g. 'en', 'vi'")
    page_count: int = Field(1, ge=1)

    model_version: Optional[str] = None
    processing_time: Optional[float] = Field(None, description="Processing duration in seconds")
    error_message: Optional[str] = None

    created_at: datetime

# ------------- Response (lightweight status check) ---------------
class OcrStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: DocumentStatus
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

# ------------- Response (Markdown only) ---------------
class OcrMarkdownResponse(BaseModel):
    document_id: uuid.UUID
    markdown_output: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    page_count: int = 1
    processing_time: Optional[float] = None