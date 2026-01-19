"""MinIO storage service for file management."""
from io import BytesIO
from typing import BinaryIO, Optional
import logging

from minio import Minio
from minio.error import S3Error

from src.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage in MinIO (S3-compatible)."""
    
    def __init__(self):
        """Initialize MinIO client."""
        # Parse endpoint to extract host and port
        endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")
        secure = settings.S3_ENDPOINT.startswith("https://")
        
        self.client = Minio(
            endpoint=endpoint,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=secure,
        )
        self.bucket_name = settings.S3_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the default bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str,
        file_size: int,
        bucket_name: Optional[str] = None
    ) -> str:
        """Upload a file to MinIO.
        
        Args:
            file_data: The file data to upload
            object_name: The object name (path) in the bucket
            content_type: The MIME type of the file
            file_size: The size of the file in bytes
            bucket_name: Optional custom bucket name
            
        Returns:
            The object name (path) of the uploaded file
            
        Raises:
            S3Error: If upload fails
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
            )
            logger.info(f"Uploaded file: {object_name} to bucket: {bucket}")
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            raise
    
    def download_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> bytes:
        """Download a file from MinIO.
        
        Args:
            object_name: The object name (path) in the bucket
            bucket_name: Optional custom bucket name
            
        Returns:
            The file data as bytes
            
        Raises:
            S3Error: If download fails
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            raise
    
    def delete_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> None:
        """Delete a file from MinIO.
        
        Args:
            object_name: The object name (path) in the bucket
            bucket_name: Optional custom bucket name
            
        Raises:
            S3Error: If deletion fails
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file: {object_name} from bucket: {bucket}")
        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            raise
    
    def get_file_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        expires_in_seconds: int = 3600
    ) -> str:
        """Get a presigned URL for a file.
        
        Args:
            object_name: The object name (path) in the bucket
            bucket_name: Optional custom bucket name
            expires_in_seconds: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            A presigned URL for the file
            
        Raises:
            S3Error: If URL generation fails
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=expires_in_seconds
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating URL for {object_name}: {e}")
            raise
    
    def file_exists(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> bool:
        """Check if a file exists in MinIO.
        
        Args:
            object_name: The object name (path) in the bucket
            bucket_name: Optional custom bucket name
            
        Returns:
            True if file exists, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False
