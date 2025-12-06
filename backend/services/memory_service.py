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
        """Format search results into a context string for the AI with full audit trail"""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Build context entry with full audit trail
            entry = f"[{i}] {content}"
            
            # Add comprehensive metadata for citations and proof
            if metadata:
                meta_parts = []
                
                # Document type
                if metadata.get("type"):
                    meta_parts.append(f"📋 Type: {metadata['type'].upper()}")
                
                # Drawing reference (critical for citations)
                if metadata.get("drawing"):
                    meta_parts.append(f"📐 Drawing: {metadata['drawing']}")
                
                # Date of decision/change
                if metadata.get("date"):
                    meta_parts.append(f"📅 Date: {metadata['date']}")
                
                # WHO made the decision (audit trail)
                if metadata.get("approved_by"):
                    meta_parts.append(f"✅ Approved by: {metadata['approved_by']}")
                
                if metadata.get("requested_by"):
                    meta_parts.append(f"📝 Requested by: {metadata['requested_by']}")
                
                # WHY the decision was made (critical for disputes)
                if metadata.get("reason"):
                    meta_parts.append(f"💡 Reason: {metadata['reason']}")
                
                # Previous value (before change)
                if metadata.get("previous_value"):
                    meta_parts.append(f"⬅️ Previous: {metadata['previous_value']}")
                
                # New value (after change)
                if metadata.get("new_value"):
                    meta_parts.append(f"➡️ New: {metadata['new_value']}")
                
                # RFI/Change Order number
                if metadata.get("rfi_number"):
                    meta_parts.append(f"🔢 RFI#: {metadata['rfi_number']}")
                
                if metadata.get("change_order_number"):
                    meta_parts.append(f"🔢 CO#: {metadata['change_order_number']}")
                
                if meta_parts:
                    entry += f"\n   ({' | '.join(meta_parts)})"
            
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
            metadata: Additional metadata including:
                - drawing: Drawing reference (e.g., "ST-04")
                - approved_by: Who approved this decision
                - requested_by: Who requested this change
                - reason: Why this decision was made
                - previous_value: Old specification
                - new_value: New specification
                - rfi_number: RFI reference number
                - change_order_number: CO reference number
        
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
    
    async def add_change_order(
        self,
        project_id: str,
        description: str,
        drawing: str,
        previous_value: str,
        new_value: str,
        reason: str,
        approved_by: str,
        requested_by: Optional[str] = None,
        change_order_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a change order with full audit trail
        This creates a complete record for dispute resolution
        
        Example:
            await memory.add_change_order(
                project_id="abc123",
                description="Beam B2 depth increased",
                drawing="ST-04",
                previous_value="300x450mm",
                new_value="300x600mm",
                reason="HVAC duct clash - duct routing requires additional clearance",
                approved_by="Structural Engineer - Rajesh Kumar",
                requested_by="MEP Consultant - ABC Associates",
                change_order_number="CO-2025-047"
            )
        """
        content = f"CHANGE ORDER: {description}. Changed from {previous_value} to {new_value}. Reason: {reason}"
        
        return await self.add_document(
            project_id=project_id,
            content=content,
            doc_type="change_order",
            metadata={
                "drawing": drawing,
                "previous_value": previous_value,
                "new_value": new_value,
                "reason": reason,
                "approved_by": approved_by,
                "requested_by": requested_by,
                "change_order_number": change_order_number,
            }
        )
    
    async def add_rfi(
        self,
        project_id: str,
        question: str,
        answer: str,
        drawing: str,
        answered_by: str,
        asked_by: Optional[str] = None,
        rfi_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add an RFI (Request for Information) with full audit trail
        
        Example:
            await memory.add_rfi(
                project_id="abc123",
                question="What is the rebar spacing for slab S3?",
                answer="150mm c/c both ways, Fe500 grade",
                drawing="ST-12",
                answered_by="Structural Consultant",
                asked_by="Site Engineer - Arun",
                rfi_number="RFI-2025-089"
            )
        """
        content = f"RFI: Q: {question} | A: {answer}"
        
        return await self.add_document(
            project_id=project_id,
            content=content,
            doc_type="rfi",
            metadata={
                "drawing": drawing,
                "answered_by": answered_by,
                "asked_by": asked_by,
                "rfi_number": rfi_number,
            }
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

