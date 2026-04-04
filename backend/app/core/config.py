from __future__ import annotations

import json
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──
    APP_NAME: str = "NanoOCR"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Database ──
    DATABASE_URL: str = "postgresql://ocr_user:ocr_pass@localhost:5433/ocr_db"

    # ── Redis / Celery ──
    REDIS_URL: str = "redis://localhost:6380/0"
    CELERY_BROKER_URL: str = "redis://localhost:6380/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6380/1"

    # ── Storage (MinIO / S3) ──
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "ocr-documents"
    STORAGE_USE_SSL: bool = False

    # ── Ollama ─────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OCR_MODEL_NAME: str = "adelnazmy2002/Qwen3-VL-4B-Instruct:Q4_K_M" 
    OCR_MAX_NEW_TOKENS: int = 2048

    # ── Upload ─────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".pdf"
    ]

    # ── Validators ─────────────────────────────────────────
    @field_validator("ALLOWED_ORIGINS", "ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_list_field(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


# @lru_cache  # removed to fix caching issue
def get_settings() -> Settings:
    return Settings()


settings = get_settings()