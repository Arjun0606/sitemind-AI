"""
SiteMind Memory Service - Unlimited Project Context
Uses Supermemory.ai for semantic search across ALL project history

WHY SUPERMEMORY:
- Gemini 3.0 Pro has 1M token context per query
- But projects accumulate YEARS of data (RFIs, COs, decisions)
- Supermemory stores EVERYTHING, returns only what's relevant
- Result: Effectively UNLIMITED memory with perfect recall

FLOW:
1. All RFIs, change orders, decisions → stored in Supermemory
2. Engineer asks question on WhatsApp
3. Search Supermemory for relevant context
4. Feed context + blueprints to Gemini 3.0
5. AI answers with full citations

Supermemory: https://supermemory.ai
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
    Supermemory-powered long-term memory for construction projects
    Stores and retrieves RFIs, change orders, decisions with full audit trail
    """
    
    SUPERMEMORY_BASE_URL = "https://api.supermemory.ai/v1"
    
    def __init__(self):
        """Initialize memory service"""
        self.api_key = settings.supermemory_api_key
        self.is_configured = bool(self.api_key)
        
        # Fallback in-memory storage (for local dev/testing)
        self._memory_store: Dict[str, List[Dict[str, Any]]] = {}
        
        if self.is_configured:
            logger.info("✅ Memory service: Supermemory.ai connected (unlimited context)")
        else:
            logger.warning("⚠️ Memory service: Using local fallback (set SUPERMEMORY_API_KEY for production)")
    
    async def add_memory(
        self,
        project_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a memory to the project's knowledge base
        
        This gets stored permanently and can be retrieved semantically.
        Think of it as adding to the project's "brain".
        
        Args:
            project_id: Project/site identifier (e.g., "skyline_towers_block_a")
            content: Text content to store (will be embedded for search)
            metadata: Structured data for citations (type, date, approved_by, etc.)
        
        Returns:
            Dict with memory_id and status
        """
        start_time = time.time()
        
        memory_entry = {
            "id": f"mem_{int(time.time() * 1000)}_{project_id[:8]}",
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "project_id": project_id,
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
                                "project_id": project_id,
                                **(metadata or {}),
                            },
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    logger.info(f"📝 Memory added to Supermemory: {project_id} ({elapsed_ms}ms)")
                    
                    return {
                        "memory_id": result.get("id", memory_entry["id"]),
                        "status": "success",
                        "provider": "supermemory",
                        "response_time_ms": elapsed_ms,
                    }
                    
            except Exception as e:
                logger.error(f"Supermemory error, falling back to local: {e}")
        
        # Fallback to in-memory storage
        if project_id not in self._memory_store:
            self._memory_store[project_id] = []
        
        self._memory_store[project_id].append(memory_entry)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"📝 Memory added locally: {project_id} ({elapsed_ms}ms)")
        
        return {
            "memory_id": memory_entry["id"],
            "status": "success",
            "provider": "local",
            "response_time_ms": elapsed_ms,
        }
    
    async def search_memory(
        self,
        project_id: str,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic search across project memory
        
        This is the magic - finds relevant context from YEARS of project history
        using semantic similarity, not just keyword matching.
        
        Args:
            project_id: Project identifier
            query: Natural language query (e.g., "beam B2 changes")
            limit: Max results (default 10, enough context without overwhelming)
            memory_types: Filter by type (e.g., ["change_order", "rfi"])
        
        Returns:
            Dict with results and formatted context string for Gemini
        """
        start_time = time.time()
        
        if self.is_configured:
            try:
                # Build filter
                filter_obj = {"namespace": project_id}
                if memory_types:
                    filter_obj["type"] = {"$in": memory_types}
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.SUPERMEMORY_BASE_URL}/search",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "query": query,
                            "filter": filter_obj,
                            "limit": limit,
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    results = result.get("results", [])
                    context = self._format_context_for_gemini(results)
                    
                    logger.info(f"🔍 Supermemory search: {len(results)} results for '{query[:50]}...' ({elapsed_ms}ms)")
                    
                    return {
                        "results": results,
                        "context": context,
                        "count": len(results),
                        "provider": "supermemory",
                        "response_time_ms": elapsed_ms,
                    }
                    
            except Exception as e:
                logger.error(f"Supermemory search error: {e}")
        
        # Fallback to local keyword search
        memories = self._memory_store.get(project_id, [])
        
        # Simple keyword matching
        query_words = set(query.lower().split())
        scored_memories = []
        
        for mem in memories:
            content_words = set(mem["content"].lower().split())
            # Also search in metadata
            meta_str = str(mem.get("metadata", {})).lower()
            meta_words = set(meta_str.split())
            all_words = content_words | meta_words
            
            score = len(query_words & all_words) / max(len(query_words), 1)
            
            # Filter by type if specified
            if memory_types:
                mem_type = mem.get("metadata", {}).get("type")
                if mem_type not in memory_types:
                    continue
            
            if score > 0:
                scored_memories.append((score, mem))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = [mem for _, mem in scored_memories[:limit]]
        
        context = self._format_context_for_gemini(results)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"🔍 Local search: {len(results)} results ({elapsed_ms}ms)")
        
        return {
            "results": results,
            "context": context,
            "count": len(results),
            "provider": "local",
            "response_time_ms": elapsed_ms,
        }
    
    def _format_context_for_gemini(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context string optimized for Gemini 3.0
        
        Gemini 3.0 prefers structured, clear context with citations
        """
        if not results:
            return ""
        
        context_parts = ["**RELEVANT PROJECT HISTORY:**\n"]
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Build structured entry
            entry_parts = [f"**[{i}]** {content}"]
            
            # Add citation metadata (critical for audit trail)
            citations = []
            
            if metadata.get("type"):
                type_emoji = {
                    "change_order": "🔄",
                    "rfi": "❓",
                    "decision": "✅",
                    "meeting_notes": "📋",
                    "rework": "⚠️",
                    "approval": "✅",
                }.get(metadata["type"], "📝")
                citations.append(f"{type_emoji} {metadata['type'].upper()}")
            
            if metadata.get("drawing"):
                citations.append(f"📐 {metadata['drawing']}")
            
            if metadata.get("date"):
                citations.append(f"📅 {metadata['date']}")
            
            if metadata.get("approved_by"):
                citations.append(f"✅ Approved: {metadata['approved_by']}")
            
            if metadata.get("reason"):
                citations.append(f"💡 Reason: {metadata['reason']}")
            
            if metadata.get("previous_value") and metadata.get("new_value"):
                citations.append(f"⬅️ {metadata['previous_value']} → ➡️ {metadata['new_value']}")
            
            if metadata.get("rfi_number"):
                citations.append(f"RFI#{metadata['rfi_number']}")
            
            if metadata.get("change_order_number"):
                citations.append(f"CO#{metadata['change_order_number']}")
            
            if citations:
                entry_parts.append(f"   _({' | '.join(citations)})_")
            
            context_parts.append("\n".join(entry_parts))
        
        return "\n\n".join(context_parts)
    
    # =========================================================================
    # CONVENIENCE METHODS FOR COMMON DOCUMENT TYPES
    # =========================================================================
    
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
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a change order with full audit trail
        
        Example:
            await memory.add_change_order(
                project_id="skyline_towers",
                description="Beam B2 depth increased for HVAC clearance",
                drawing="ST-04, Grid B2",
                previous_value="300x450mm",
                new_value="300x600mm",
                reason="HVAC duct routing requires 200mm additional clearance",
                approved_by="Structural Engineer - Rajesh Kumar",
                requested_by="MEP Consultant - ABC Associates",
                change_order_number="CO-2024-047"
            )
        """
        content = f"CHANGE ORDER: {description}. Drawing {drawing} changed from {previous_value} to {new_value}. Reason: {reason}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            metadata={
                "type": "change_order",
                "drawing": drawing,
                "previous_value": previous_value,
                "new_value": new_value,
                "reason": reason,
                "approved_by": approved_by,
                "requested_by": requested_by,
                "change_order_number": change_order_number,
                "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
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
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record an RFI (Request for Information)
        
        Example:
            await memory.add_rfi(
                project_id="skyline_towers",
                question="What is the rebar spacing for cantilever slab S3?",
                answer="150mm c/c both ways, Fe500D grade, with 12mm dia bars",
                drawing="ST-12, Detail D4",
                answered_by="Structural Consultant - XYZ Associates",
                asked_by="Site Engineer - Arun",
                rfi_number="RFI-2024-089"
            )
        """
        content = f"RFI: Question: {question} | Answer: {answer}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            metadata={
                "type": "rfi",
                "question": question,
                "answer": answer,
                "drawing": drawing,
                "answered_by": answered_by,
                "asked_by": asked_by,
                "rfi_number": rfi_number,
                "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
            }
        )
    
    async def add_decision(
        self,
        project_id: str,
        decision: str,
        context: str,
        made_by: str,
        drawing: Optional[str] = None,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a project decision
        
        Example:
            await memory.add_decision(
                project_id="skyline_towers",
                decision="Use Fe500D instead of Fe550D for all slabs",
                context="Supply constraints - Fe550D not available from approved vendors",
                made_by="Site PM with Structural Consultant approval",
                drawing="All slab drawings"
            )
        """
        content = f"DECISION: {decision}. Context: {context}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            metadata={
                "type": "decision",
                "decision": decision,
                "context": context,
                "approved_by": made_by,
                "drawing": drawing,
                "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
            }
        )
    
    async def add_rework(
        self,
        project_id: str,
        description: str,
        location: str,
        cause: str,
        estimated_cost: Optional[str] = None,
        preventive_action: Optional[str] = None,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a rework incident (for learning and ROI tracking)
        
        Example:
            await memory.add_rework(
                project_id="skyline_towers",
                description="Floor 2 slab demolished and repoured",
                location="Floor 2, Grid A1-B3",
                cause="Level error - slab was 50mm higher than specification",
                estimated_cost="₹2.5 Lakhs",
                preventive_action="Implemented level verification checklist"
            )
        """
        content = f"REWORK: {description} at {location}. Cause: {cause}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            metadata={
                "type": "rework",
                "description": description,
                "location": location,
                "cause": cause,
                "estimated_cost": estimated_cost,
                "preventive_action": preventive_action,
                "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
            }
        )
    
    async def add_whatsapp_query(
        self,
        project_id: str,
        question: str,
        answer: str,
        engineer_phone: str,
        engineer_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Store a WhatsApp Q&A for future reference
        
        This helps the AI learn what questions are common and
        provides context for follow-up questions.
        """
        content = f"WhatsApp Q&A: Q: {question} | A: {answer}"
        
        return await self.add_memory(
            project_id=project_id,
            content=content,
            metadata={
                "type": "whatsapp_query",
                "question": question,
                "answer": answer,
                "engineer_phone": engineer_phone,
                "engineer_name": engineer_name,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            }
        )
    
    # =========================================================================
    # RETRIEVAL AND MANAGEMENT
    # =========================================================================
    
    async def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get summary of what's stored for a project"""
        memories = await self.get_project_memories(project_id, limit=1000)
        
        summary = {
            "project_id": project_id,
            "total_memories": len(memories),
            "by_type": {},
        }
        
        for mem in memories:
            mem_type = mem.get("metadata", {}).get("type", "other")
            summary["by_type"][mem_type] = summary["by_type"].get(mem_type, 0) + 1
        
        return summary
    
    async def get_project_memories(
        self,
        project_id: str,
        limit: int = 100,
        memory_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all memories for a project"""
        if self.is_configured:
            try:
                params = {"namespace": project_id, "limit": limit}
                if memory_type:
                    params["type"] = memory_type
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.SUPERMEMORY_BASE_URL}/memories",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        params=params,
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    return response.json().get("memories", [])
                    
            except Exception as e:
                logger.error(f"Failed to get memories: {e}")
        
        # Fallback
        memories = self._memory_store.get(project_id, [])
        if memory_type:
            memories = [m for m in memories if m.get("metadata", {}).get("type") == memory_type]
        return memories[:limit]
    
    async def delete_memory(self, project_id: str, memory_id: str) -> bool:
        """Delete a specific memory"""
        if self.is_configured:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"{self.SUPERMEMORY_BASE_URL}/memories/{memory_id}",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    logger.info(f"🗑️ Memory deleted: {memory_id}")
                    return True
            except Exception as e:
                logger.error(f"Failed to delete memory: {e}")
                return False
        
        # Fallback
        if project_id in self._memory_store:
            original_len = len(self._memory_store[project_id])
            self._memory_store[project_id] = [
                m for m in self._memory_store[project_id]
                if m.get("id") != memory_id
            ]
            return len(self._memory_store[project_id]) < original_len
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check memory service health"""
        if not self.is_configured:
            return {
                "status": "fallback",
                "provider": "local",
                "message": "Using in-memory storage (set SUPERMEMORY_API_KEY for production)"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.SUPERMEMORY_BASE_URL}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "provider": "supermemory",
                        "message": "Connected to Supermemory.ai (unlimited context)"
                    }
                return {"status": "degraded", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "provider": "supermemory", "error": str(e)}


# Singleton instance
memory_service = MemoryService()
