"""
SiteMind Storage Service
File storage using Supabase Storage

FEATURES:
- Upload documents (drawings, PDFs)
- Upload images (site photos)
- Generate signed URLs
- Organize by project
"""

from typing import Optional, Dict, Any
import httpx
import base64
from datetime import datetime

from config import settings
from utils.logger import logger


class StorageService:
    """
    File storage using Supabase Storage
    """
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_KEY
        self.bucket = settings.STORAGE_BUCKET
        
        # In-memory fallback for development
        self._local_files: Dict[str, Dict] = {}
    
    async def upload_document(
        self,
        project_id: str,
        file_content: bytes,
        file_name: str,
        content_type: str,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Upload a document to storage
        
        Args:
            project_id: Project identifier
            file_content: File bytes
            file_name: Original filename
            content_type: MIME type
            user_id: Who uploaded
            
        Returns:
            Upload result with path and URL
        """
        # Generate storage path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = file_name.replace(" ", "_").lower()
        path = f"{project_id}/documents/{timestamp}_{safe_name}"
        
        # Try Supabase
        if self.supabase_url and self.supabase_url != "your_supabase_url":
            try:
                result = await self._upload_to_supabase(path, file_content, content_type)
                logger.info(f"📁 Document uploaded to Supabase: {path}")
                return result
            except Exception as e:
                logger.warning(f"Supabase upload error, using local: {e}")
        
        # Local fallback
        file_id = f"file_{datetime.utcnow().timestamp():.0f}"
        self._local_files[file_id] = {
            "id": file_id,
            "path": path,
            "name": file_name,
            "content_type": content_type,
            "size": len(file_content),
            "project_id": project_id,
            "uploaded_by": user_id,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"📁 Document stored locally: {path}")
        
        return {
            "id": file_id,
            "path": path,
            "url": f"/api/files/{file_id}",
            "name": file_name,
        }
    
    async def upload_image(
        self,
        project_id: str,
        image_content: bytes,
        file_name: str,
        image_type: str = "progress",
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Upload an image to storage
        
        Args:
            project_id: Project identifier
            image_content: Image bytes
            file_name: Original filename
            image_type: progress, issue, drawing, etc.
            user_id: Who uploaded
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"{project_id}/images/{image_type}/{timestamp}_{file_name}"
        
        # Try Supabase
        if self.supabase_url and self.supabase_url != "your_supabase_url":
            try:
                result = await self._upload_to_supabase(path, image_content, "image/jpeg")
                logger.info(f"📷 Image uploaded to Supabase: {path}")
                return result
            except Exception as e:
                logger.warning(f"Supabase upload error, using local: {e}")
        
        # Local fallback
        file_id = f"img_{datetime.utcnow().timestamp():.0f}"
        self._local_files[file_id] = {
            "id": file_id,
            "path": path,
            "name": file_name,
            "content_type": "image/jpeg",
            "size": len(image_content),
            "project_id": project_id,
            "image_type": image_type,
            "uploaded_by": user_id,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"📷 Image stored locally: {path}")
        
        return {
            "id": file_id,
            "path": path,
            "url": f"/api/files/{file_id}",
            "name": file_name,
        }
    
    async def download_from_url(self, url: str) -> bytes:
        """Download file from external URL (e.g., Twilio media)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed to download: {response.status_code}")
    
    async def get_signed_url(self, path: str, expires_in: int = 3600) -> str:
        """Get a signed URL for file access"""
        if self.supabase_url and self.supabase_url != "your_supabase_url":
            try:
                return await self._get_supabase_signed_url(path, expires_in)
            except Exception as e:
                logger.warning(f"Supabase signed URL error: {e}")
        
        # Return local path
        return f"/api/files/download?path={path}"
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        """Get file metadata by ID"""
        return self._local_files.get(file_id)
    
    async def list_project_files(
        self,
        project_id: str,
        file_type: str = None,
    ) -> list:
        """List files for a project"""
        files = [
            f for f in self._local_files.values()
            if f.get("project_id") == project_id
        ]
        
        if file_type:
            files = [f for f in files if f.get("content_type", "").startswith(file_type)]
        
        return sorted(files, key=lambda x: x.get("uploaded_at", ""), reverse=True)
    
    # =========================================================================
    # SUPABASE METHODS
    # =========================================================================
    
    async def _upload_to_supabase(
        self,
        path: str,
        content: bytes,
        content_type: str,
    ) -> Dict:
        """Upload to Supabase Storage"""
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": content_type,
                },
                content=content,
            )
            
            if response.status_code in [200, 201]:
                return {
                    "path": path,
                    "url": f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{path}",
                }
            else:
                raise Exception(f"Supabase upload error: {response.status_code}")
    
    async def _get_supabase_signed_url(self, path: str, expires_in: int) -> str:
        """Get signed URL from Supabase"""
        url = f"{self.supabase_url}/storage/v1/object/sign/{self.bucket}/{path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.supabase_key}"},
                json={"expiresIn": expires_in},
            )
            
            if response.status_code == 200:
                return response.json().get("signedURL")
            else:
                raise Exception(f"Supabase signed URL error: {response.status_code}")


# Singleton instance
storage_service = StorageService()
