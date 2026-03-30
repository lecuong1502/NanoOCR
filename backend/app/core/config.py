from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ----------- App -----------
    APP_NAME: str = "NanoOCR"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ----------- Database ------------
    DATABASE_URL: str = "postgresql://ocr_user:ocr_pass@localhost:5433/ocr_db"

    # ----------- Redis / Celery ------------
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ----------- Storage (MiniIO / S3) -------------
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "ocr-documents"
    STORAGE_USE_SSL: bool = False

    # ----------- GLM-OCR Model -------------
    GLM_OCR_MODEL_PATH: str = "./models/glm-ocr"
    GLM_OCR_DEVICE: str = "cuda"          # cuda | cpu
    GLM_OCR_MAX_NEW_TOKENS: int = 2048
    GLM_OCR_BATCH_SIZE: int = 1

    # ----------- Upload -------------
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".pdf"
    ]

@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of Settings."""
    return Settings()

# Convenient module-level import: from app.core.config import settings
settings = get_settings()