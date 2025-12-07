"""
SiteMind Supabase Client
Database and Storage operations

SETUP:
1. Create Supabase project at supabase.com
2. Run schema.sql in SQL editor
3. Create storage buckets: documents, photos, exports
4. Add API keys to .env
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx

from config import settings
from utils.logger import logger


class SupabaseClient:
    """
    Supabase client for database and storage
    """
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.service_key = settings.SUPABASE_SERVICE_KEY
        
        # Use service key for backend operations
        self.headers = {
            "apikey": self.service_key or self.key,
            "Authorization": f"Bearer {self.service_key or self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        
        self.rest_url = f"{self.url}/rest/v1"
        self.storage_url = f"{self.url}/storage/v1"
    
    def _is_configured(self) -> bool:
        """Check if Supabase is configured"""
        return (
            self.url and
            self.url != "your_supabase_url" and
            "supabase" in self.url
        )
    
    # =========================================================================
    # GENERIC CRUD
    # =========================================================================
    
    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Dict = None,
        order: str = None,
        limit: int = None,
    ) -> List[Dict]:
        """Select from table"""
        if not self._is_configured():
            logger.warning(f"Supabase not configured, returning empty for {table}")
            return []
        
        url = f"{self.rest_url}/{table}?select={columns}"
        
        if filters:
            for key, value in filters.items():
                url += f"&{key}=eq.{value}"
        
        if order:
            url += f"&order={order}"
        
        if limit:
            url += f"&limit={limit}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Supabase select error: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return []
    
    async def insert(self, table: str, data: Dict) -> Optional[Dict]:
        """Insert into table"""
        if not self._is_configured():
            logger.warning(f"Supabase not configured, skipping insert to {table}")
            return None
        
        url = f"{self.rest_url}/{table}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=data)
                if response.status_code in [200, 201]:
                    result = response.json()
                    return result[0] if isinstance(result, list) else result
                else:
                    logger.error(f"Supabase insert error: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return None
    
    async def update(self, table: str, filters: Dict, data: Dict) -> Optional[Dict]:
        """Update table"""
        if not self._is_configured():
            return None
        
        url = f"{self.rest_url}/{table}"
        
        for key, value in filters.items():
            url += f"?{key}=eq.{value}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self.headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result[0] if isinstance(result, list) and result else result
                else:
                    logger.error(f"Supabase update error: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return None
    
    async def delete(self, table: str, filters: Dict) -> bool:
        """Delete from table"""
        if not self._is_configured():
            return False
        
        url = f"{self.rest_url}/{table}"
        
        for key, value in filters.items():
            url += f"?{key}=eq.{value}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=self.headers)
                return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return False
    
    # =========================================================================
    # COMPANIES
    # =========================================================================
    
    async def create_company(
        self,
        name: str,
        gstin: str = None,
        billing_email: str = None,
        is_pilot: bool = False,
    ) -> Optional[Dict]:
        """Create a new company"""
        return await self.insert("companies", {
            "name": name,
            "gstin": gstin,
            "billing_email": billing_email,
            "is_pilot": is_pilot,
            "is_founding": is_pilot,  # Pilots become founding customers
        })
    
    async def get_company(self, company_id: str) -> Optional[Dict]:
        """Get company by ID"""
        results = await self.select("companies", filters={"id": company_id})
        return results[0] if results else None
    
    async def get_company_by_user_phone(self, phone: str) -> Optional[Dict]:
        """Get company by user's phone number"""
        users = await self.select("users", filters={"phone": phone})
        if users:
            return await self.get_company(users[0]["company_id"])
        return None
    
    # =========================================================================
    # PROJECTS
    # =========================================================================
    
    async def create_project(
        self,
        company_id: str,
        name: str,
        location: str = None,
        project_type: str = "residential",
    ) -> Optional[Dict]:
        """Create a new project"""
        return await self.insert("projects", {
            "company_id": company_id,
            "name": name,
            "location": location,
            "project_type": project_type,
            "stage": "active",
        })
    
    async def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        results = await self.select("projects", filters={"id": project_id})
        return results[0] if results else None
    
    async def get_company_projects(self, company_id: str) -> List[Dict]:
        """Get all projects for a company"""
        return await self.select(
            "projects",
            filters={"company_id": company_id},
            order="created_at.desc"
        )
    
    # =========================================================================
    # USERS
    # =========================================================================
    
    async def create_user(
        self,
        company_id: str,
        name: str,
        phone: str,
        role: str = "site_engineer",
        email: str = None,
    ) -> Optional[Dict]:
        """Create a new user"""
        return await self.insert("users", {
            "company_id": company_id,
            "name": name,
            "phone": phone,
            "role": role,
            "email": email,
        })
    
    async def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """Get user by phone number"""
        results = await self.select("users", filters={"phone": phone})
        return results[0] if results else None
    
    async def get_company_users(self, company_id: str) -> List[Dict]:
        """Get all users for a company"""
        return await self.select("users", filters={"company_id": company_id})
    
    async def update_user_activity(self, user_id: str):
        """Update user's last active timestamp"""
        await self.update("users", {"id": user_id}, {
            "last_active_at": datetime.utcnow().isoformat(),
        })
    
    # =========================================================================
    # QUERIES (for billing)
    # =========================================================================
    
    async def log_query(
        self,
        company_id: str,
        project_id: str,
        user_id: str,
        question: str,
        answer: str,
        query_type: str = None,
        response_time_ms: int = None,
    ) -> Optional[Dict]:
        """Log a query for billing"""
        billing_cycle = datetime.utcnow().strftime("%Y-%m")
        
        return await self.insert("queries", {
            "company_id": company_id,
            "project_id": project_id,
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "query_type": query_type,
            "response_time_ms": response_time_ms,
            "billing_cycle": billing_cycle,
            "billed": False,
        })
    
    async def get_cycle_queries(self, company_id: str, billing_cycle: str) -> List[Dict]:
        """Get queries for a billing cycle"""
        return await self.select(
            "queries",
            filters={"company_id": company_id, "billing_cycle": billing_cycle}
        )
    
    async def count_cycle_queries(self, company_id: str, billing_cycle: str) -> int:
        """Count queries for a billing cycle"""
        queries = await self.get_cycle_queries(company_id, billing_cycle)
        return len(queries)
    
    # =========================================================================
    # DOCUMENTS
    # =========================================================================
    
    async def log_document(
        self,
        company_id: str,
        project_id: str,
        user_id: str,
        name: str,
        file_path: str,
        file_type: str,
        file_size_bytes: int,
        extracted_text: str = None,
    ) -> Optional[Dict]:
        """Log a document upload"""
        billing_cycle = datetime.utcnow().strftime("%Y-%m")
        
        return await self.insert("documents", {
            "company_id": company_id,
            "project_id": project_id,
            "uploaded_by": user_id,
            "name": name,
            "file_path": file_path,
            "file_type": file_type,
            "file_size_bytes": file_size_bytes,
            "extracted_text": extracted_text,
            "billing_cycle": billing_cycle,
            "billed": False,
        })
    
    async def count_cycle_documents(self, company_id: str, billing_cycle: str) -> int:
        """Count documents for a billing cycle"""
        docs = await self.select(
            "documents",
            filters={"company_id": company_id, "billing_cycle": billing_cycle}
        )
        return len(docs)
    
    # =========================================================================
    # PHOTOS
    # =========================================================================
    
    async def log_photo(
        self,
        company_id: str,
        project_id: str,
        user_id: str,
        file_path: str,
        file_size_bytes: int,
        caption: str = None,
        analysis: str = None,
        photo_type: str = None,
        location: str = None,
    ) -> Optional[Dict]:
        """Log a photo upload"""
        billing_cycle = datetime.utcnow().strftime("%Y-%m")
        
        return await self.insert("photos", {
            "company_id": company_id,
            "project_id": project_id,
            "uploaded_by": user_id,
            "file_path": file_path,
            "file_size_bytes": file_size_bytes,
            "caption": caption,
            "analysis": analysis,
            "photo_type": photo_type,
            "location": location,
            "billing_cycle": billing_cycle,
            "billed": False,
        })
    
    async def count_cycle_photos(self, company_id: str, billing_cycle: str) -> int:
        """Count photos for a billing cycle"""
        photos = await self.select(
            "photos",
            filters={"company_id": company_id, "billing_cycle": billing_cycle}
        )
        return len(photos)
    
    # =========================================================================
    # USAGE & BILLING
    # =========================================================================
    
    async def get_or_create_usage(self, company_id: str, billing_cycle: str) -> Dict:
        """Get or create usage record for a billing cycle"""
        results = await self.select(
            "usage",
            filters={"company_id": company_id, "billing_cycle": billing_cycle}
        )
        
        if results:
            return results[0]
        
        # Create new usage record
        year, month = billing_cycle.split("-")
        cycle_start = f"{year}-{month}-01"
        
        # Calculate cycle end
        if int(month) == 12:
            cycle_end = f"{int(year)+1}-01-01"
        else:
            cycle_end = f"{year}-{int(month)+1:02d}-01"
        
        return await self.insert("usage", {
            "company_id": company_id,
            "billing_cycle": billing_cycle,
            "cycle_start": cycle_start,
            "cycle_end": cycle_end,
        })
    
    async def update_usage_counts(self, company_id: str, billing_cycle: str) -> Dict:
        """Update usage counts from actual data"""
        queries = await self.count_cycle_queries(company_id, billing_cycle)
        documents = await self.count_cycle_documents(company_id, billing_cycle)
        photos = await self.count_cycle_photos(company_id, billing_cycle)
        
        # Get current usage record
        usage = await self.get_or_create_usage(company_id, billing_cycle)
        
        # Calculate overages
        queries_overage = max(0, queries - usage.get("queries_included", 500))
        documents_overage = max(0, documents - usage.get("documents_included", 20))
        photos_overage = max(0, photos - usage.get("photos_included", 100))
        
        # Calculate charges
        usage_charges = (
            queries_overage * 0.15 +
            documents_overage * 2.50 +
            photos_overage * 0.50
        )
        
        total = usage.get("flat_fee_usd", 500) + usage_charges
        
        # Update
        return await self.update("usage", {"id": usage["id"]}, {
            "queries_count": queries,
            "documents_count": documents,
            "photos_count": photos,
            "queries_overage": queries_overage,
            "documents_overage": documents_overage,
            "photos_overage": photos_overage,
            "usage_charges_usd": usage_charges,
            "total_usd": total,
        })
    
    # =========================================================================
    # STORAGE
    # =========================================================================
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_content: bytes,
        content_type: str,
    ) -> Optional[str]:
        """Upload file to Supabase Storage"""
        if not self._is_configured():
            logger.warning("Supabase not configured, skipping file upload")
            return None
        
        url = f"{self.storage_url}/object/{bucket}/{path}"
        
        headers = {
            "apikey": self.service_key or self.key,
            "Authorization": f"Bearer {self.service_key or self.key}",
            "Content-Type": content_type,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, content=file_content)
                if response.status_code in [200, 201]:
                    return f"{self.url}/storage/v1/object/public/{bucket}/{path}"
                else:
                    logger.error(f"Storage upload error: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Storage error: {e}")
            return None
    
    async def get_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> Optional[str]:
        """Get signed URL for private file"""
        if not self._is_configured():
            return None
        
        url = f"{self.storage_url}/object/sign/{bucket}/{path}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json={"expiresIn": expires_in}
                )
                if response.status_code == 200:
                    return response.json().get("signedURL")
                return None
        except Exception as e:
            logger.error(f"Storage error: {e}")
            return None
    
    # =========================================================================
    # AUDIT LOG
    # =========================================================================
    
    async def log_audit(
        self,
        company_id: str,
        action: str,
        description: str,
        project_id: str = None,
        user_id: str = None,
        old_value: Dict = None,
        new_value: Dict = None,
    ):
        """Log an audit entry"""
        await self.insert("audit_log", {
            "company_id": company_id,
            "project_id": project_id,
            "user_id": user_id,
            "action": action,
            "description": description,
            "old_value": old_value,
            "new_value": new_value,
        })


# Singleton instance
db = SupabaseClient()

