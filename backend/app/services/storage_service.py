from __future__ import annotations

import os
import uuid
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.exceptions import StorageException
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.STORAGE_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=settings.STORAGE_ACCESS_KEY,
            secret_key=settings.STORAGE_SECRET_KEY,
            secure=settings.STORAGE_USE_SSL,
        )
        # Ensure bucket exists
        if not _client.bucket_exists(settings.STORAGE_BUCKET):
            _client.make_bucket(settings.STORAGE_BUCKET)
            logger.info(f"Created bucket: {settings.STORAGE_BUCKET}")
    return _client


def upload_file(
    file_data: BinaryIO,
    filename: str,
    content_type: str,
    size: int,
) -> str:
    """Upload a file to MinIO and return its storage path."""
    client = get_minio_client()
    ext = os.path.splitext(filename)[1].lower()
    object_name = f"{uuid.uuid4()}{ext}"

    try:
        client.put_object(
            bucket_name=settings.STORAGE_BUCKET,
            object_name=object_name,
            data=file_data,
            length=size,
            content_type=content_type,
        )
        logger.info(f"Uploaded file: {object_name}")
        return object_name
    except S3Error as e:
        logger.error(f"MinIO upload error: {e}")
        raise StorageException(f"Failed to upload file: {e}")
    

def get_file_url(object_name: str, expires_hours: int = 24) -> str:
    """Generate a presigned download URL valid for the given hours."""
    from datetime import timedelta
    client = get_minio_client()
    try:
        return client.presigned_get_object(
            bucket_name=settings.STORAGE_BUCKET,
            object_name=object_name,
            expires=timedelta(hours=expires_hours),
        )
    except S3Error as e:
        return StorageException(f"Failed to generate URL: {e}")
    

def download_file(object_name: str) -> bytes:
    """Download raw bytes from MinIO."""
    client = get_minio_client()
    try:
        response = client.get_object(settings.STORAGE_BUCKET, object_name)
        return response.read()
    except S3Error as e:
        raise StorageException(f"Failed to download file: {e}")
    finally:
        response.close()
        response.release_conn()


def delete_file(object_name: str) -> None:
    """Delete a file from MinIO."""
    client = get_minio_client()
    try:
        client.remove_object(settings.STORAGE_BUCKET, object_name)
        logger.info(f"Deleted file: {object_name}")
    except S3Error as e:
        raise StorageException(f"Failed to delete file: {e}")