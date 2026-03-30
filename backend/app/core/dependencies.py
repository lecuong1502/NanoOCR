from fastapi import Depends, UploadFile
from sqlalchemy.orm import Session

from db.session import get_db
from app.core.config import settings
from app.core.exceptions import UnsupportedFileTypeException, FileTooLargeException

import os

def get_database() -> Session:
    """Re-export get_db for use in routers via Depends(get_database)."""
    return next(get_db())

async def validate_upload_file(file: UploadFile) -> UploadFile:
    """Dependency that validates file type and size before processing."""

    # Check extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeException(ext)

    # Check file size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise FileTooLargeException(settings.MAX_UPLOAD_SIZE_MB)

    # Reset stream so downstream handlers can re-read the file
    await file.seek()

    return file