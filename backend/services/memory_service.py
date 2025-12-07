"""
SiteMind Memory Service
Long-term project memory using Supermemory.ai

SUPERMEMORY INTEGRATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Docs: https://supermemory.ai/docs/introduction

Key Concepts:
- Add memories: Store project knowledge
- Search: Semantic search across all memories
- User profiles: Per-project memory spaces

API Endpoints Used:
- POST /v1/memories - Add a memory
- POST /v1/search - Search memories
- DELETE /v1/memories/{id} - Delete memory

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
import json

from config import settings
from utils.logger import logger


class MemoryService:
    """
    Supermemory.ai integration for long-term project memory
    
    Each project gets its own memory space (using metadata filtering)
    """
    
    def __init__(self):
        self.api_key = settings.SUPERMEMORY_API_KEY
        self.base_url = "https://api.supermemory.ai/v1"
        
        # Headers for API calls
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Local fallback for development
        self._local_memories: Dict[str, List[Dict]] = {}
    
    def _is_configured(self) -> bool:
        """Check if Supermemory is configured"""
        return (
            self.api_key and 
            self.api_key != "your_supermemory_api_key" and
            len(self.api_key) > 10
        )
    
    # =========================================================================
    # ADD MEMORIES
    # =========================================================================
    
    async def add_memory(
        self,
        project_id: str,
        content: str,
        memory_type: str,
        metadata: Dict = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add a memory to the project
        
        Args:
            project_id: Project identifier (used for filtering)
            content: The content to remember
            memory_type: Type of memory (decision, query, document, etc.)
            metadata: Additional structured data
            user_id: Who added this memory
            
        Returns:
            Memory record with ID
        """
        memory_data = {
            "content": content,
            "metadata": {
                "project_id": project_id,
                "type": memory_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {}),
            },
        }
        
        if self._is_configured():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/memories",
                        headers=self.headers,
                        json=memory_data,
                        timeout=30.0,
                    )
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        logger.info(f"💾 Memory added to Supermemory: {content[:50]}...")
                        return {
                            "id": result.get("id"),
                            "status": "stored",
                            "provider": "supermemory",
                            **memory_data,
                        }
                    else:
                        logger.error(f"Supermemory error: {response.status_code} - {response.text}")
                        
            except Exception as e:
                logger.error(f"Supermemory API error: {e}")
        
        # Fallback to local storage
        return self._add_local(project_id, memory_data)
    
    def _add_local(self, project_id: str, memory_data: Dict) -> Dict:
        """Add to local memory (fallback)"""
        if project_id not in self._local_memories:
            self._local_memories[project_id] = []
        
        memory = {
            "id": f"local_{datetime.utcnow().timestamp():.0f}",
            "status": "stored_locally",
            "provider": "local",
            **memory_data,
        }
        
        self._local_memories[project_id].append(memory)
        logger.info(f"💾 Memory added locally: {memory_data['content'][:50]}...")
        
        return memory
    
    # =========================================================================
    # SEARCH MEMORIES
    # =========================================================================
    
    async def search(
        self,
        project_id: str,
        query: str,
        limit: int = 5,
        memory_types: List[str] = None,
    ) -> List[Dict]:
        """
        Search memories for a project
        
        Args:
            project_id: Project to search in
            query: Search query (semantic search)
            limit: Max results
            memory_types: Filter by type (decision, query, etc.)
            
        Returns:
            List of matching memories
        """
        if self._is_configured():
            try:
                async with httpx.AsyncClient() as client:
                    search_payload = {
                        "query": query,
                        "limit": limit,
                        "filter": {
                            "project_id": project_id,
                        },
                    }
                    
                    if memory_types:
                        search_payload["filter"]["type"] = {"$in": memory_types}
                    
                    response = await client.post(
                        f"{self.base_url}/search",
                        headers=self.headers,
                        json=search_payload,
                        timeout=30.0,
                    )
                    
                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        logger.info(f"🔍 Supermemory search: '{query[:30]}...' → {len(results)} results")
                        return results
                    else:
                        logger.error(f"Supermemory search error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Supermemory search error: {e}")
        
        # Fallback to local search
        return self._search_local(project_id, query, limit)
    
    def _search_local(self, project_id: str, query: str, limit: int) -> List[Dict]:
        """Search local memories (fallback)"""
        memories = self._local_memories.get(project_id, [])
        
        # Simple keyword matching
        query_lower = query.lower()
        query_words = query_lower.split()
        
        scored = []
        for memory in memories:
            content = memory.get("content", "").lower()
            
            # Score by keyword matches
            score = sum(1 for word in query_words if word in content)
            if score > 0:
                scored.append((score, memory))
        
        # Sort by score descending
        scored.sort(key=lambda x: -x[0])
        
        results = [m for _, m in scored[:limit]]
        logger.info(f"🔍 Local search: '{query[:30]}...' → {len(results)} results")
        
        return results
    
    # =========================================================================
    # SPECIALIZED ADD METHODS
    # =========================================================================
    
    async def add_decision(
        self,
        project_id: str,
        decision: str,
        reason: str = None,
        approved_by: str = None,
        affected_area: str = None,
        user_id: str = None,
    ) -> Dict:
        """Add a project decision"""
        content = f"Decision: {decision}"
        if reason:
            content += f"\nReason: {reason}"
        if approved_by:
            content += f"\nApproved by: {approved_by}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            memory_type="decision",
            metadata={
                "decision": decision,
                "reason": reason,
                "approved_by": approved_by,
                "affected_area": affected_area,
            },
            user_id=user_id,
        )
    
    async def add_change_order(
        self,
        project_id: str,
        description: str,
        old_spec: str,
        new_spec: str,
        reason: str = None,
        user_id: str = None,
    ) -> Dict:
        """Add a change order"""
        content = f"Change Order: {description}\n"
        content += f"Changed from: {old_spec}\n"
        content += f"Changed to: {new_spec}"
        if reason:
            content += f"\nReason: {reason}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            memory_type="change_order",
            metadata={
                "description": description,
                "old_spec": old_spec,
                "new_spec": new_spec,
                "reason": reason,
            },
            user_id=user_id,
        )
    
    async def add_rfi(
        self,
        project_id: str,
        question: str,
        answer: str = None,
        asked_by: str = None,
        answered_by: str = None,
        user_id: str = None,
    ) -> Dict:
        """Add an RFI (Request for Information)"""
        content = f"RFI: {question}"
        if answer:
            content += f"\nAnswer: {answer}"
            if answered_by:
                content += f"\n(Answered by {answered_by})"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            memory_type="rfi",
            metadata={
                "question": question,
                "answer": answer,
                "asked_by": asked_by,
                "answered_by": answered_by,
                "status": "answered" if answer else "pending",
            },
            user_id=user_id,
        )
    
    async def add_query(
        self,
        project_id: str,
        question: str,
        answer: str,
        user_id: str = None,
    ) -> Dict:
        """Add a Q&A from WhatsApp"""
        content = f"Q: {question}\nA: {answer}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            memory_type="query",
            metadata={
                "question": question,
                "answer": answer,
            },
            user_id=user_id,
        )
    
    async def add_document(
        self,
        project_id: str,
        document_name: str,
        document_type: str,
        extracted_text: str,
        file_path: str = None,
        user_id: str = None,
    ) -> Dict:
        """Add document content to memory"""
        content = f"Document: {document_name}\n"
        content += f"Type: {document_type}\n"
        content += f"Content:\n{extracted_text}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            memory_type="document",
            metadata={
                "document_name": document_name,
                "document_type": document_type,
                "file_path": file_path,
            },
            user_id=user_id,
        )
    
    # =========================================================================
    # CONTEXT RETRIEVAL
    # =========================================================================
    
    async def get_context(
        self,
        project_id: str,
        query: str,
        include_types: List[str] = None,
    ) -> List[Dict]:
        """
        Get relevant context for answering a query
        
        Combines:
        - Semantic search results
        - Recent decisions
        - Recent change orders
        """
        # Search for relevant memories
        search_results = await self.search(
            project_id=project_id,
            query=query,
            limit=5,
            memory_types=include_types,
        )
        
        # Also get recent important items
        if not include_types or "decision" in include_types:
            decisions = await self.search(
                project_id=project_id,
                query="decision change",
                limit=3,
                memory_types=["decision", "change_order"],
            )
            
            # Merge and dedupe
            seen_ids = {r.get("id") for r in search_results}
            for d in decisions:
                if d.get("id") not in seen_ids:
                    search_results.append(d)
        
        return search_results[:7]  # Max 7 context items
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_stats(self, project_id: str) -> Dict[str, int]:
        """Get memory stats for a project"""
        memories = self._local_memories.get(project_id, [])
        
        stats = {
            "total": len(memories),
            "decisions": 0,
            "change_orders": 0,
            "rfis": 0,
            "queries": 0,
            "documents": 0,
        }
        
        for m in memories:
            mem_type = m.get("metadata", {}).get("type", "other")
            if mem_type in stats:
                stats[mem_type] += 1
        
        return stats


# Singleton instance
memory_service = MemoryService()
