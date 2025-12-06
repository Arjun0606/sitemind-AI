"""
SiteMind Storage Service
Supabase Storage integration for blueprint and media file storage
Much simpler than AWS S3 for solo developers!
"""

import time
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import httpx

from config import settings
from utils.logger import logger
from utils.helpers import sanitize_filename, generate_unique_id


class StorageService:
    """
    Supabase Storage Service
    Handles blueprint uploads, downloads, and public URLs
    
    Supabase Storage is much simpler than S3:
    - No complex IAM policies
    - Built-in CDN
    - Same dashboard as your database
    """
    
    # Allowed file types for blueprints
    ALLOWED_EXTENSIONS = {'.pdf', '.dwg', '.dxf', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (Supabase free tier limit)
    
    BUCKET_NAME = "blueprints"
    
    def __init__(self):
        """Initialize Supabase storage service"""
        if not settings.supabase_url or not settings.supabase_service_key:
            logger.warning("Supabase credentials not configured")
            self.is_configured = False
            self.supabase = None
            return
        
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_key  # Use service key for storage admin
            )
            self.is_configured = True
            logger.info("Supabase storage service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            self.is_configured = False
            self.supabase = None
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        project_id: str,
        category: str = "other",
    ) -> Dict[str, Any]:
        """
        Upload a file to Supabase Storage
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            project_id: Project UUID
            category: File category (architectural, structural, mep, etc.)
        
        Returns:
            Dict with file_url, storage_path, file_size
        """
        if not self.is_configured:
            return {
                "file_url": None,
                "storage_path": None,
                "error": "Storage service not configured"
            }
        
        start_time = time.time()
        
        try:
            # Validate file
            ext = Path(filename).suffix.lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                return {
                    "file_url": None,
                    "storage_path": None,
                    "error": f"File type {ext} not allowed"
                }
            
            if len(file_content) > self.MAX_FILE_SIZE:
                return {
                    "file_url": None,
                    "storage_path": None,
                    "error": f"File size exceeds {self.MAX_FILE_SIZE // 1024 // 1024}MB limit"
                }
            
            # Generate storage path
            safe_filename = sanitize_filename(filename)
            unique_id = generate_unique_id()[:8]
            storage_path = f"{project_id}/{category}/{unique_id}_{safe_filename}"
            
            # Determine content type
            content_type = self._get_content_type(ext)
            
            # Upload to Supabase Storage
            result = await asyncio.to_thread(
                self.supabase.storage.from_(self.BUCKET_NAME).upload,
                storage_path,
                file_content,
                {"content-type": content_type}
            )
            
            # Get public URL
            file_url = self.supabase.storage.from_(self.BUCKET_NAME).get_public_url(storage_path)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"File uploaded to Supabase: {storage_path} ({len(file_content)} bytes, {elapsed_ms}ms)")
            
            return {
                "file_url": file_url,
                "storage_path": storage_path,
                "file_size": len(file_content),
                "content_type": content_type,
                "response_time_ms": elapsed_ms,
            }
            
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            return {
                "file_url": None,
                "storage_path": None,
                "error": str(e)
            }
    
    async def download_file(self, storage_path: str) -> Optional[bytes]:
        """
        Download a file from Supabase Storage
        
        Args:
            storage_path: Path in storage bucket
        
        Returns:
            File content as bytes, or None if failed
        """
        if not self.is_configured:
            return None
        
        try:
            result = await asyncio.to_thread(
                self.supabase.storage.from_(self.BUCKET_NAME).download,
                storage_path
            )
            return result
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None
    
    async def get_public_url(self, storage_path: str) -> Optional[str]:
        """
        Get public URL for a file
        
        Args:
            storage_path: Path in storage bucket
        
        Returns:
            Public URL or None
        """
        if not self.is_configured:
            return None
        
        try:
            return self.supabase.storage.from_(self.BUCKET_NAME).get_public_url(storage_path)
        except Exception as e:
            logger.error(f"Failed to get public URL: {e}")
            return None
    
    async def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from Supabase Storage
        
        Args:
            storage_path: Path in storage bucket
        
        Returns:
            True if deleted, False otherwise
        """
        if not self.is_configured:
            return False
        
        try:
            await asyncio.to_thread(
                self.supabase.storage.from_(self.BUCKET_NAME).remove,
                [storage_path]
            )
            logger.info(f"File deleted from Supabase: {storage_path}")
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
            
            result = await asyncio.to_thread(
                self.supabase.storage.from_(self.BUCKET_NAME).list,
                prefix
            )
            
            files = []
            for item in result:
                if item.get('name'):
                    storage_path = f"{prefix}{item['name']}"
                    files.append({
                        'storage_path': storage_path,
                        'name': item['name'],
                        'size': item.get('metadata', {}).get('size', 0),
                        'created_at': item.get('created_at'),
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def _get_content_type(self, ext: str) -> str:
        """Get MIME type from extension"""
        mapping = {
            '.pdf': 'application/pdf',
            '.dwg': 'application/acad',
            '.dxf': 'application/dxf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }
        return mapping.get(ext, 'application/octet-stream')
    
    async def ensure_bucket_exists(self) -> bool:
        """
        Ensure the blueprints bucket exists (call on startup)
        """
        if not self.is_configured:
            return False
        
        try:
            # Try to create bucket (will fail silently if exists)
            await asyncio.to_thread(
                self.supabase.storage.create_bucket,
                self.BUCKET_NAME,
                {"public": True}  # Public bucket for blueprint access
            )
            logger.info(f"Storage bucket '{self.BUCKET_NAME}' ready")
            return True
        except Exception as e:
            # Bucket might already exist, that's fine
            if "already exists" in str(e).lower():
                logger.info(f"Storage bucket '{self.BUCKET_NAME}' already exists")
                return True
            logger.error(f"Failed to create bucket: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if storage service is healthy"""
        if not self.is_configured:
            return {"status": "not_configured", "error": "Supabase credentials not set"}
        
        try:
            # Try to list buckets
            buckets = await asyncio.to_thread(
                self.supabase.storage.list_buckets
            )
            return {
                "status": "healthy",
                "provider": "supabase",
                "bucket": self.BUCKET_NAME,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
storage_service = StorageService()
