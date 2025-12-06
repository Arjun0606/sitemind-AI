"""
SiteMind Storage Service
AWS S3 integration for blueprint and media file storage
"""

import time
import asyncio
import mimetypes
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

from config import settings
from utils.logger import logger
from utils.helpers import sanitize_filename, generate_unique_id


class StorageService:
    """
    AWS S3 Storage Service
    Handles blueprint uploads, downloads, and pre-signed URLs
    """
    
    # Allowed file types for blueprints
    ALLOWED_EXTENSIONS = {'.pdf', '.dwg', '.dxf', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(self):
        """Initialize S3 storage service"""
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            logger.warning("AWS credentials not configured")
            self.is_configured = False
            return
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket = settings.aws_s3_bucket
        self.is_configured = True
        
        logger.info(f"Storage service initialized with bucket: {self.bucket}")
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        project_id: str,
        category: str = "other",
    ) -> Dict[str, Any]:
        """
        Upload a file to S3
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            project_id: Project UUID
            category: File category (architectural, structural, mep, etc.)
        
        Returns:
            Dict with file_url, s3_key, file_size
        """
        if not self.is_configured:
            return {
                "file_url": None,
                "s3_key": None,
                "error": "Storage service not configured"
            }
        
        start_time = time.time()
        
        try:
            # Validate file
            ext = Path(filename).suffix.lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                return {
                    "file_url": None,
                    "s3_key": None,
                    "error": f"File type {ext} not allowed"
                }
            
            if len(file_content) > self.MAX_FILE_SIZE:
                return {
                    "file_url": None,
                    "s3_key": None,
                    "error": f"File size exceeds {self.MAX_FILE_SIZE // 1024 // 1024}MB limit"
                }
            
            # Generate S3 key
            safe_filename = sanitize_filename(filename)
            unique_id = generate_unique_id()[:8]
            s3_key = f"{project_id}/{category}/{unique_id}_{safe_filename}"
            
            # Determine content type
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Upload to S3
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'project_id': project_id,
                    'category': category,
                    'original_filename': filename,
                    'uploaded_at': datetime.utcnow().isoformat(),
                }
            )
            
            # Generate the S3 URL
            file_url = f"https://{self.bucket}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"File uploaded to S3: {s3_key} ({len(file_content)} bytes, {elapsed_ms}ms)")
            
            return {
                "file_url": file_url,
                "s3_key": s3_key,
                "file_size": len(file_content),
                "content_type": content_type,
                "response_time_ms": elapsed_ms,
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return {
                "file_url": None,
                "s3_key": None,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {
                "file_url": None,
                "s3_key": None,
                "error": str(e)
            }
    
    async def upload_file_object(
        self,
        file: BinaryIO,
        filename: str,
        project_id: str,
        category: str = "other",
    ) -> Dict[str, Any]:
        """
        Upload a file object to S3
        
        Args:
            file: File-like object
            filename: Original filename
            project_id: Project UUID
            category: File category
        
        Returns:
            Dict with upload result
        """
        content = file.read()
        return await self.upload_file(content, filename, project_id, category)
    
    async def download_file(self, s3_key: str) -> Optional[bytes]:
        """
        Download a file from S3
        
        Args:
            s3_key: S3 object key
        
        Returns:
            File content as bytes, or None if failed
        """
        if not self.is_configured:
            return None
        
        try:
            response = await asyncio.to_thread(
                self.s3_client.get_object,
                Bucket=self.bucket,
                Key=s3_key,
            )
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None
    
    async def get_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
    ) -> Optional[str]:
        """
        Generate a pre-signed URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration in seconds (default 1 hour)
        
        Returns:
            Pre-signed URL or None if failed
        """
        if not self.is_configured:
            return None
        
        try:
            url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key,
                },
                ExpiresIn=expiration,
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 object key
        
        Returns:
            True if deleted, False otherwise
        """
        if not self.is_configured:
            return False
        
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket,
                Key=s3_key,
            )
            logger.info(f"File deleted from S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def list_project_files(
        self,
        project_id: str,
        category: Optional[str] = None,
    ) -> list:
        """
        List all files for a project
        
        Args:
            project_id: Project UUID
            category: Optional category filter
        
        Returns:
            List of file info dicts
        """
        if not self.is_configured:
            return []
        
        try:
            prefix = f"{project_id}/"
            if category:
                prefix = f"{project_id}/{category}/"
            
            response = await asyncio.to_thread(
                self.s3_client.list_objects_v2,
                Bucket=self.bucket,
                Prefix=prefix,
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    's3_key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'filename': Path(obj['Key']).name,
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3"""
        if not self.is_configured:
            return False
        
        try:
            await asyncio.to_thread(
                self.s3_client.head_object,
                Bucket=self.bucket,
                Key=s3_key,
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking file: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if storage service is healthy"""
        if not self.is_configured:
            return {"status": "not_configured", "error": "AWS credentials not set"}
        
        try:
            # Try to list bucket (head_bucket)
            await asyncio.to_thread(
                self.s3_client.head_bucket,
                Bucket=self.bucket,
            )
            return {
                "status": "healthy",
                "bucket": self.bucket,
                "region": settings.aws_region,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
storage_service = StorageService()

