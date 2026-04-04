from __future__ import annotations

import uuid

from celery import Task
from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app
from app.models.document import DocumentStatus

logger = get_task_logger(__name__)


class OcrTask(Task):
    """Base task class that holds DB session and services as class-level singletons.
    They are initialized once per worker process, not per task call.
    """
    abstract = True
    _db = None

    @property
    def db(self):
        if self._db is None:
            from sqlalchemy.orm import sessionmaker
            from app.db.session import get_engine
            engine = get_engine()
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        """Close DB session after each task regardless of outcome."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=OcrTask,
    name="app.tasks.ocr_tasks.run_ocr",
    max_retries=3,
    default_retry_delay=15,
    soft_time_limit=300,   # 5 min soft limit  → raises SoftTimeLimitExceeded
    time_limit=360,        # 6 min hard limit  → kills task process
)
def run_ocr(self, document_id: str) -> dict:
    """
    Celery task: download file from storage → run Qwen3-VL OCR → persist result.

    Args:
        document_id: UUID string of the document to process.

    Returns:
        dict with document_id, status, and processing_time.
    """
    from app.services import document_service, ocr_result_service
    from app.services.ocr_service import process_image, process_pdf
    from app.services.storage_service import download_file

    doc_uuid = uuid.UUID(document_id)
    logger.info(f"[OCR] Starting task for document: {document_id}")

    # ------ Mark as PROCESSING ------
    try:
        doc = document_service.get_document(self.db, doc_uuid)
        doc.status = DocumentStatus.PROCESSING
        self.db.commit()
    except Exception as exc:
        logger.error(f"[OCR] Document not found: {document_id} — {exc}")
        raise

    # ------ Download file from MinIO ------
    try:
        file_bytes = download_file(doc.file_path)
        logger.info(f"[OCR] Downloaded {len(file_bytes)} bytes for {document_id}")
    except Exception as exc:
        logger.error(f"[OCR] Download failed: {exc}")
        ocr_result_service.save_ocr_error(self.db, doc, f"Download failed: {exc}")
        raise self.retry(exc=exc)
    
    # ------ Run OCR ------
    try:
        if doc.file_type.value == "pdf":
            output = process_pdf(file_bytes)
        else:
            output = process_image(file_bytes, mime_type=doc.mime_type or "image/jpeg")
        logger.info(
            f"[OCR] Inference done — pages={output.page_count} "
            f"time={output.processing_time}s confidence={output.confidence}"
        )
    except Exception as exc:
        logger.error(f"[OCR] Inference failed: {exc}")
        ocr_result_service.save_ocr_error(self.db, doc, f"OCR inference failed: {exc}")
        raise self.retry(exc=exc)
    
    # ------ Persist result ------
    try:
        result = ocr_result_service.create_or_update_ocr_result(self.db, doc, output)
        logger.info(f"[OCR] Result saved: {result.id}")
    except Exception as exc:
        logger.error(f"[OCR] Failed to save result: {exc}")
        raise self.retry(exc=exc)
    
    return {
        "document_id": document_id,
        "status": DocumentStatus.DONE.value,
        "processing_time": output.processing_time,
        "page_count": output.page_count,
    }
    

@celery_app.task(name="app.tasks.ocr_tasks.health_check")
def health_check() -> dict:
    """Simple ping task to verify the worker is alive."""
    return {"status": "ok"}