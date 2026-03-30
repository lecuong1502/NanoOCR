from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ocr_result import OcrResult

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, BigInteger, Enum as SAEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
import enum

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class DocumentFileType(str, enum.Enum):
    IMAGE = "image"
    PDF = "pdf"

class Document(Base):
    __tablename__ = "documents"

    # ------------ Primary Key --------------
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ------------ File metadata --------------
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_type: Mapped[DocumentFileType] = mapped_column(
        SAEnum(DocumentFileType, name="document_file_type"),
        nullable=False,
    )
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ------------ Processing state -------------
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status"),
        nullable=False,
        default=DocumentStatus.PENDING,
        index=True,
    )

    # ------------ Ownership --------------
    uploaded_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ------------ Timestamps -------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ------------ Relationships --------------
    ocr_result: Mapped["OcrResult"] = relationship(
        "OcrResult",
        back_populates="document",
        uselist=False,          # one-to-one
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} name={self.name!r} status={self.status}>"