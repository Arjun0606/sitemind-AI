"""
SiteMind Memory Service
Long-term memory management using Supermemory or a simpler vector store fallback
"""

import time
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from config import settings
from utils.logger import logger


class MemoryService:
    """
    Memory Service for SiteMind
    Provides long-term memory for project context, RFIs, change orders, etc.
    
    Uses Supermemory.ai API or falls back to simple in-memory storage for MVP
    """
    
    SUPERMEMORY_BASE_URL = "https://api.supermemory.ai/v1"
    
    def __init__(self):
        """Initialize memory service"""
        self.api_key = settings.supermemory_api_key
        self.is_configured = bool(self.api_key)
        
        # Fallback in-memory storage for MVP (will be replaced with Supermemory)
        self._memory_store: Dict[str, List[Dict[str, Any]]] = {}
        
        if self.is_configured:
            logger.info("Memory service initialized with Supermemory")
        else:
            logger.warning("Supermemory not configured, using fallback in-memory storage")
    
    async def add_memory(
        self,
        project_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a memory to the project's knowledge base
        
        Args:
            project_id: Project/namespace identifier
            content: Text content to store
            metadata: Additional metadata (type, date, drawing reference, etc.)
        
        Returns:
            Dict with memory_id and status
        """
        start_time = time.time()
        
        memory_entry = {
            "id": f"mem_{int(time.time() * 1000)}",
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        if self.is_configured:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.SUPERMEMORY_BASE_URL}/memories",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "content": content,
                            "metadata": {
                                "namespace": project_id,
                                **(metadata or {}),
                            },
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    logger.info(f"Memory added via Supermemory in {elapsed_ms}ms")
                    
                    return {
                        "memory_id": result.get("id", memory_entry["id"]),
                        "status": "success",
                        "response_time_ms": elapsed_ms,
                    }
                    
            except Exception as e:
                logger.error(f"Supermemory error, falling back to local: {e}")
                # Fall through to local storage
        
        # Fallback to in-memory storage
        if project_id not in self._memory_store:
            self._memory_store[project_id] = []
        
        self._memory_store[project_id].append(memory_entry)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Memory added locally in {elapsed_ms}ms")
        
        return {
            "memory_id": memory_entry["id"],
            "status": "success",
            "response_time_ms": elapsed_ms,
        }
    
    async def search_memory(
        self,
        project_id: str,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Search project memory for relevant context
        
        Args:
            project_id: Project/namespace identifier
            query: Search query
            limit: Maximum number of results
        
        Returns:
            Dict with results and formatted context string
        """
        start_time = time.time()
        
        if self.is_configured:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.SUPERMEMORY_BASE_URL}/search",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "query": query,
                            "filter": {
                                "namespace": project_id,
                            },
                            "limit": limit,
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    
                    # Format results into context string
                    results = result.get("results", [])
                    context = self._format_context(results)
                    
                    logger.info(f"Memory search via Supermemory: {len(results)} results in {elapsed_ms}ms")
                    
                    return {
                        "results": results,
                        "context": context,
                        "count": len(results),
                        "response_time_ms": elapsed_ms,
                    }
                    
            except Exception as e:
                logger.error(f"Supermemory search error, falling back to local: {e}")
                # Fall through to local search
        
        # Fallback to simple local search
        memories = self._memory_store.get(project_id, [])
        
        # Simple keyword matching (in production, use vector similarity)
        query_words = set(query.lower().split())
        scored_memories = []
        
        for mem in memories:
            content_words = set(mem["content"].lower().split())
            score = len(query_words & content_words) / max(len(query_words), 1)
            if score > 0:
                scored_memories.append((score, mem))
        
        # Sort by score and take top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = [mem for _, mem in scored_memories[:limit]]
        
        context = self._format_context(results)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"Memory search locally: {len(results)} results in {elapsed_ms}ms")
        
        return {
            "results": results,
            "context": context,
            "count": len(results),
            "response_time_ms": elapsed_ms,
        }
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into a context string for the AI"""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Build context entry
            entry = f"[{i}] {content}"
            
            # Add metadata if available
            if metadata:
                meta_parts = []
                if metadata.get("type"):
                    meta_parts.append(f"Type: {metadata['type']}")
                if metadata.get("date"):
                    meta_parts.append(f"Date: {metadata['date']}")
                if metadata.get("drawing"):
                    meta_parts.append(f"Drawing: {metadata['drawing']}")
                if meta_parts:
                    entry += f"\n   ({', '.join(meta_parts)})"
            
            context_parts.append(entry)
        
        return "\n\n".join(context_parts)
    
    async def add_document(
        self,
        project_id: str,
        content: str,
        doc_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a document to memory (RFI, Change Order, Meeting Notes, etc.)
        
        Args:
            project_id: Project identifier
            content: Document content
            doc_type: Type of document (rfi, change_order, meeting_notes, etc.)
            metadata: Additional metadata
        
        Returns:
            Dict with document_id and status
        """
        full_metadata = {
            "type": doc_type,
            "date": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            metadata=full_metadata,
        )
    
    async def get_project_memories(
        self,
        project_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a project
        
        Args:
            project_id: Project identifier
            limit: Maximum number of results
        
        Returns:
            List of memory entries
        """
        if self.is_configured:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.SUPERMEMORY_BASE_URL}/memories",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                        },
                        params={
                            "namespace": project_id,
                            "limit": limit,
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    return response.json().get("memories", [])
                    
            except Exception as e:
                logger.error(f"Failed to get memories: {e}")
        
        # Fallback to local storage
        return self._memory_store.get(project_id, [])[:limit]
    
    async def delete_memory(
        self,
        project_id: str,
        memory_id: str,
    ) -> bool:
        """Delete a specific memory"""
        if self.is_configured:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"{self.SUPERMEMORY_BASE_URL}/memories/{memory_id}",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    return True
            except Exception as e:
                logger.error(f"Failed to delete memory: {e}")
                return False
        
        # Fallback to local deletion
        if project_id in self._memory_store:
            self._memory_store[project_id] = [
                m for m in self._memory_store[project_id]
                if m.get("id") != memory_id
            ]
            return True
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if memory service is healthy"""
        if not self.is_configured:
            return {
                "status": "fallback",
                "message": "Using in-memory storage (Supermemory not configured)"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.SUPERMEMORY_BASE_URL}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return {"status": "healthy", "provider": "supermemory"}
                return {"status": "degraded", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
memory_service = MemoryService()

