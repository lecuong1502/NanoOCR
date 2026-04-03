from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "nanoocr",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.ocr_tasks"],
)

celery_app.conf.update(
    # ------ Serialization ------
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # ------ Timezone ------
    timezone="UTC",
    enable_utc=True,

    # ------ Task behavior ------
    task_acks_late=True,              # ACK only after task completes
    task_reject_on_worker_lost=True,  # Re-queue if worker crashes mid-task
    task_track_started=True,          # Mark task as STARTED when worker picks it up

    # ------ Retry defaults ------
    task_max_retries=3,
    task_default_retry_delay=10,      # seconds between retries

    # ------ Result expiry ------
    result_expires=60 * 60 * 24,      # keep results for 24 hours

    # ------ Worker ------
    worker_prefetch_multiplier=1,     # one task at a time per worker (OCR is heavy)
    worker_max_tasks_per_child=50,    # restart worker process after 50 tasks (prevent memory leak)

    # ------ Router ------
    task_routes={
        "app.tasks.ocr_tasks.run_ocr": {"queue": "ocr"},
    },
)