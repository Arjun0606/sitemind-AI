"""
SiteMind Memory Service
Long-term project memory using Supermemory.ai (with local fallback)

FEATURES:
- Store project knowledge (decisions, specs, queries)
- Semantic search across all project data
- Automatic context retrieval
- Audit trail with citations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import httpx

from config import settings
from utils.logger import logger


class MemoryService:
    """
    Project memory management using Supermemory.ai
    Falls back to in-memory storage for development
    """
    
    def __init__(self):
        self.api_key = settings.SUPERMEMORY_API_KEY
        self.base_url = "https://api.supermemory.ai/v1"
        
        # In-memory fallback for development
        self._local_memory: Dict[str, List[Dict]] = {}
    
    async def add(
        self,
        project_id: str,
        content: str,
        content_type: str,
        metadata: Dict = None,
        source: str = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add content to project memory
        
        Args:
            project_id: Project identifier
            content: Text content to store
            content_type: Type (decision, change_order, rfi, query, instruction, etc.)
            metadata: Additional structured data
            source: Where this came from (whatsapp, dashboard, email)
            user_id: Who added this
            
        Returns:
            Memory record with ID
        """
        memory_record = {
            "id": f"mem_{datetime.utcnow().timestamp():.0f}",
            "project_id": project_id,
            "content": content,
            "content_type": content_type,
            "metadata": metadata or {},
            "source": source or "unknown",
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Try Supermemory API
        if self.api_key and self.api_key != "your_supermemory_api_key":
            try:
                result = await self._add_to_supermemory(project_id, memory_record)
                logger.info(f"💾 Memory added to Supermemory: {content[:50]}...")
                return result
            except Exception as e:
                logger.warning(f"Supermemory error, using local: {e}")
        
        # Fallback to local memory
        if project_id not in self._local_memory:
            self._local_memory[project_id] = []
        
        self._local_memory[project_id].append(memory_record)
        logger.info(f"💾 Memory added locally: {content[:50]}...")
        
        return memory_record
    
    async def search(
        self,
        project_id: str,
        query: str,
        limit: int = 5,
        content_types: List[str] = None,
    ) -> List[Dict]:
        """
        Search project memory
        
        Args:
            project_id: Project identifier
            query: Search query
            limit: Maximum results
            content_types: Filter by type (decision, query, etc.)
            
        Returns:
            List of matching memory records
        """
        # Try Supermemory API
        if self.api_key and self.api_key != "your_supermemory_api_key":
            try:
                results = await self._search_supermemory(project_id, query, limit)
                logger.info(f"🔍 Supermemory search: {query[:30]}... ({len(results)} results)")
                return results
            except Exception as e:
                logger.warning(f"Supermemory search error, using local: {e}")
        
        # Fallback to local search
        memories = self._local_memory.get(project_id, [])
        
        # Simple keyword matching
        query_lower = query.lower()
        matches = []
        
        for mem in memories:
            content = mem.get("content", "").lower()
            if query_lower in content or any(word in content for word in query_lower.split()):
                if content_types is None or mem.get("content_type") in content_types:
                    matches.append(mem)
        
        # Sort by recency
        matches.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        logger.info(f"🔍 Local search: {query[:30]}... ({len(matches[:limit])} results)")
        
        return matches[:limit]
    
    async def add_decision(
        self,
        project_id: str,
        decision: str,
        reason: str = None,
        approved_by: str = None,
        affected_area: str = None,
        old_value: str = None,
        new_value: str = None,
        user_id: str = None,
        source: str = "whatsapp",
    ) -> Dict[str, Any]:
        """
        Add a project decision to memory
        """
        content = f"Decision: {decision}"
        if reason:
            content += f"\nReason: {reason}"
        if old_value and new_value:
            content += f"\nChanged from: {old_value} to: {new_value}"
        
        metadata = {
            "decision": decision,
            "reason": reason,
            "approved_by": approved_by,
            "affected_area": affected_area,
            "old_value": old_value,
            "new_value": new_value,
        }
        
        return await self.add(
            project_id=project_id,
            content=content,
            content_type="decision",
            metadata=metadata,
            source=source,
            user_id=user_id,
        )
    
    async def add_change_order(
        self,
        project_id: str,
        description: str,
        affected_element: str,
        old_spec: str = None,
        new_spec: str = None,
        reason: str = None,
        approved_by: str = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add a change order to memory
        """
        content = f"Change Order: {description}\n"
        content += f"Element: {affected_element}\n"
        if old_spec:
            content += f"Previous: {old_spec}\n"
        if new_spec:
            content += f"New: {new_spec}\n"
        if reason:
            content += f"Reason: {reason}"
        
        metadata = {
            "description": description,
            "affected_element": affected_element,
            "old_spec": old_spec,
            "new_spec": new_spec,
            "reason": reason,
            "approved_by": approved_by,
        }
        
        return await self.add(
            project_id=project_id,
            content=content,
            content_type="change_order",
            metadata=metadata,
            source="whatsapp",
            user_id=user_id,
        )
    
    async def add_rfi(
        self,
        project_id: str,
        question: str,
        from_user: str,
        to_consultant: str = None,
        response: str = None,
        response_by: str = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add an RFI to memory
        """
        content = f"RFI: {question}\n"
        content += f"From: {from_user}\n"
        if to_consultant:
            content += f"To: {to_consultant}\n"
        if response:
            content += f"Response: {response}\n"
            if response_by:
                content += f"Answered by: {response_by}"
        
        metadata = {
            "question": question,
            "from_user": from_user,
            "to_consultant": to_consultant,
            "response": response,
            "response_by": response_by,
            "status": "answered" if response else "pending",
        }
        
        return await self.add(
            project_id=project_id,
            content=content,
            content_type="rfi",
            metadata=metadata,
            source="whatsapp",
            user_id=user_id,
        )
    
    async def add_whatsapp_query(
        self,
        project_id: str,
        question: str,
        answer: str,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add a WhatsApp Q&A to memory for context
        """
        content = f"Q: {question}\nA: {answer}"
        
        metadata = {
            "question": question,
            "answer": answer,
        }
        
        return await self.add(
            project_id=project_id,
            content=content,
            content_type="query",
            metadata=metadata,
            source="whatsapp",
            user_id=user_id,
        )
    
    async def add_document(
        self,
        project_id: str,
        document_name: str,
        document_type: str,
        extracted_content: str,
        file_path: str = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add document content to memory
        """
        content = f"Document: {document_name}\n"
        content += f"Type: {document_type}\n"
        content += f"Content:\n{extracted_content}"
        
        metadata = {
            "document_name": document_name,
            "document_type": document_type,
            "file_path": file_path,
        }
        
        return await self.add(
            project_id=project_id,
            content=content,
            content_type="document",
            metadata=metadata,
            source="upload",
            user_id=user_id,
        )
    
    async def get_context_for_query(
        self,
        project_id: str,
        query: str,
    ) -> List[Dict]:
        """
        Get relevant context for answering a query
        """
        # Search for relevant memories
        results = await self.search(project_id, query, limit=5)
        
        # Also get recent decisions and change orders
        all_memories = self._local_memory.get(project_id, [])
        recent_decisions = [
            m for m in all_memories
            if m.get("content_type") in ["decision", "change_order"]
        ][-3:]  # Last 3
        
        # Combine, deduplicate
        seen_ids = set()
        combined = []
        
        for item in results + recent_decisions:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                combined.append(item)
        
        return combined[:5]
    
    # =========================================================================
    # SUPERMEMORY API METHODS
    # =========================================================================
    
    async def _add_to_supermemory(self, project_id: str, record: Dict) -> Dict:
        """Add memory to Supermemory API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/memories",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "content": record["content"],
                    "metadata": {
                        **record["metadata"],
                        "project_id": project_id,
                        "content_type": record["content_type"],
                        "source": record["source"],
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise Exception(f"Supermemory error: {response.status_code}")
    
    async def _search_supermemory(self, project_id: str, query: str, limit: int) -> List[Dict]:
        """Search Supermemory API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "query": query,
                    "limit": limit,
                    "filter": {
                        "project_id": project_id,
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                raise Exception(f"Supermemory search error: {response.status_code}")
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_memory_stats(self, project_id: str) -> Dict[str, int]:
        """Get memory statistics for a project"""
        memories = self._local_memory.get(project_id, [])
        
        stats = {
            "total": len(memories),
            "decisions": 0,
            "change_orders": 0,
            "rfis": 0,
            "queries": 0,
            "documents": 0,
        }
        
        for mem in memories:
            content_type = mem.get("content_type", "other")
            if content_type in stats:
                stats[content_type] += 1
        
        return stats


# Singleton instance
memory_service = MemoryService()
