"""
SiteMind Storage Service
File storage using Supabase Storage

BUCKETS:
- documents: PDFs, drawings, specs
- photos: Site photos
- exports: Generated reports
"""

from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import uuid

from config import settings
from utils.logger import logger


class StorageService:
    """
    Supabase Storage wrapper
    """
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
        self.storage_url = f"{self.url}/storage/v1"
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
        }
        
        # Local fallback storage
        self._local_files: Dict[str, bytes] = {}
    
    def _is_configured(self) -> bool:
        """Check if Supabase is configured"""
        return (
            self.url and
            self.url != "your_supabase_url" and
            "supabase" in self.url
        )
    
    # =========================================================================
    # UPLOAD
    # =========================================================================
    
    async def upload(
        self,
        bucket: str,
        file_content: bytes,
        file_name: str,
        content_type: str,
        company_id: str = None,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Upload file to storage
        
        Args:
            bucket: Storage bucket (documents, photos, exports)
            file_content: Raw file bytes
            file_name: Original filename
            content_type: MIME type
            company_id: For path organization
            project_id: For path organization
            
        Returns:
            Upload result with URL
        """
        # Generate unique path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Build path: company/project/timestamp_uuid_filename
        path_parts = []
        if company_id:
            path_parts.append(company_id[:8])
        if project_id:
            path_parts.append(project_id[:8])
        path_parts.append(f"{timestamp}_{unique_id}_{file_name}")
        
        path = "/".join(path_parts)
        
        if self._is_configured():
            try:
                url = f"{self.storage_url}/object/{bucket}/{path}"
                
                headers = {
                    **self.headers,
                    "Content-Type": content_type,
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers=headers,
                        content=file_content,
                        timeout=60.0,
                    )
                    
                    if response.status_code in [200, 201]:
                        public_url = f"{self.url}/storage/v1/object/public/{bucket}/{path}"
                        
                        logger.info(f"📁 Uploaded to {bucket}/{path}")
                        
                        return {
                            "status": "uploaded",
                            "path": path,
                            "bucket": bucket,
                            "url": public_url,
                            "size_bytes": len(file_content),
                        }
                    else:
                        logger.error(f"Storage error: {response.status_code} - {response.text}")
                        
            except Exception as e:
                logger.error(f"Storage upload error: {e}")
        
        # Fallback to local storage
        return self._upload_local(bucket, path, file_content)
    
    def _upload_local(self, bucket: str, path: str, content: bytes) -> Dict:
        """Local fallback storage"""
        key = f"{bucket}/{path}"
        self._local_files[key] = content
        
        logger.info(f"📁 Stored locally: {key}")
        
        return {
            "status": "stored_locally",
            "path": path,
            "bucket": bucket,
            "url": f"local://{key}",
            "size_bytes": len(content),
        }
    
    # =========================================================================
    # DOWNLOAD
    # =========================================================================
    
    async def download(self, bucket: str, path: str) -> Optional[bytes]:
        """Download file from storage"""
        if self._is_configured():
            try:
                url = f"{self.storage_url}/object/{bucket}/{path}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers, timeout=60.0)
                    
                    if response.status_code == 200:
                        return response.content
                    else:
                        logger.error(f"Storage download error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Storage download error: {e}")
        
        # Check local fallback
        key = f"{bucket}/{path}"
        return self._local_files.get(key)
    
    # =========================================================================
    # SIGNED URLS
    # =========================================================================
    
    async def get_signed_url(
        self,
        bucket: str,
        path: str,
        expires_in: int = 3600,
    ) -> Optional[str]:
        """Get a signed URL for private file access"""
        if not self._is_configured():
            return None
        
        try:
            url = f"{self.storage_url}/object/sign/{bucket}/{path}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json={"expiresIn": expires_in},
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"{self.url}/storage/v1{data.get('signedURL')}"
                    
        except Exception as e:
            logger.error(f"Signed URL error: {e}")
        
        return None
    
    # =========================================================================
    # DELETE
    # =========================================================================
    
    async def delete(self, bucket: str, path: str) -> bool:
        """Delete file from storage"""
        if not self._is_configured():
            key = f"{bucket}/{path}"
            if key in self._local_files:
                del self._local_files[key]
                return True
            return False
        
        try:
            url = f"{self.storage_url}/object/{bucket}/{path}"
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=self.headers)
                return response.status_code in [200, 204]
                
        except Exception as e:
            logger.error(f"Storage delete error: {e}")
            return False
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    async def upload_document(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        company_id: str = None,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """Upload a document (PDF, drawing, etc.)"""
        return await self.upload(
            bucket="documents",
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
            company_id=company_id,
            project_id=project_id,
        )
    
    async def upload_photo(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        company_id: str = None,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """Upload a site photo"""
        return await self.upload(
            bucket="photos",
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
            company_id=company_id,
            project_id=project_id,
        )
    
    def get_storage_usage_gb(self, company_id: str = None) -> float:
        """Get storage usage in GB (from local tracking)"""
        total_bytes = sum(
            len(content)
            for key, content in self._local_files.items()
            if not company_id or key.startswith(f"documents/{company_id}") or key.startswith(f"photos/{company_id}")
        )
        return total_bytes / (1024 ** 3)


# Singleton instance
storage_service = StorageService()
