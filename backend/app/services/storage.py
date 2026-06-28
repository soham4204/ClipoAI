"""
Storage service for interacting with MinIO.
"""
import io
from typing import BinaryIO

import structlog
from minio import Minio
from minio.error import S3Error

from app.config import settings

logger = structlog.get_logger()


class StorageService:
    """Handles object storage operations using MinIO."""

    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_use_ssl,
        )
        self.bucket = settings.minio_bucket
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create bucket if it does not exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created MinIO bucket: {self.bucket}")
        except S3Error as e:
            logger.error("Failed to ensure MinIO bucket exists", error=str(e))

    def upload_file(self, object_name: str, data: BinaryIO, length: int = -1, content_type: str = "video/mp4") -> str:
        """
        Upload a file stream to MinIO.
        Returns the object path.
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                part_size=10 * 1024 * 1024,  # 10MB parts
            )
            return f"{self.bucket}/{object_name}"
        except S3Error as e:
            logger.error("Failed to upload file to MinIO", object_name=object_name, error=str(e))
            raise

    def get_presigned_url(self, object_name: str, expires_minutes: int = 60) -> str:
        """Generate a presigned GET URL for an object."""
        try:
            from datetime import timedelta
            return self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=timedelta(minutes=expires_minutes)
            )
        except S3Error as e:
            logger.error("Failed to generate presigned URL", object_name=object_name, error=str(e))
            raise


# Singleton instance
storage_service = StorageService()
