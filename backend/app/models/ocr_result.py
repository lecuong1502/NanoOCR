from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.document import Document

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

class OcrResult(Base):
    __tablename__ = "ocr_results"

    # ---------- Primary Key ----------
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # ---------- Foreign key -> documents ----------
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,            # enforces one-to-one
        index=True,
    )

    # ---------- OCR output ----------
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    markdown_output: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- Quality metrics ----------
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default="en"
    )
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # ---------- Model info ----------
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    processing_time: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ---------- Error tracking ----------
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- Timestamp ----------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ---------- Relationship ----------
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="ocr_result",
    )

    def __repr__(self) -> str:
        return (
            f"<OcrResult id={self.id} "
            f"document_id={self.document_id} "
            f"confidence={self.confidence}>"
        )