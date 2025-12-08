"""
SiteMind Memory Service
Production-ready Supermemory.ai integration for construction project memory

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPERMEMORY.AI INTEGRATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Docs: https://supermemory.ai/docs/quickstart

Key Methods:
- client.add(content, container_tag) → Store memory
- client.profile(container_tag, q) → Search with context
- client.search(container_tag, q) → Pure search

Container Strategy:
- Each COMPANY gets a container: "company_{company_id}"
- Project-level filtering via metadata
- This allows cross-project search within a company

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import json

from config import settings
from utils.logger import logger

# Try to import supermemory SDK
try:
    from supermemory import Supermemory
    SUPERMEMORY_SDK_AVAILABLE = True
except ImportError:
    SUPERMEMORY_SDK_AVAILABLE = False
    logger.warning("Supermemory SDK not installed. Run: pip install supermemory")


@dataclass
class Memory:
    """Memory record"""
    id: str
    content: str
    memory_type: str
    project_id: str
    company_id: str
    user_id: Optional[str] = None
    metadata: Optional[Dict] = None
    timestamp: str = ""
    score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "type": self.memory_type,
            "project_id": self.project_id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "metadata": self.metadata or {},
            "timestamp": self.timestamp,
            "score": self.score,
        }


class MemoryService:
    """
    Supermemory.ai integration for long-term project memory
    
    Architecture:
    - Container per company (for billing isolation)
    - Project ID in metadata (for filtering)
    - Semantic search across all company data
    - Local fallback for development
    """
    
    def __init__(self):
        self.api_key = settings.SUPERMEMORY_API_KEY
        self.client = None
        
        # Initialize Supermemory client if available
        if SUPERMEMORY_SDK_AVAILABLE and self._is_configured():
            try:
                self.client = Supermemory(api_key=self.api_key)
                logger.info("✅ Supermemory client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supermemory: {e}")
        
        # Local fallback storage
        self._local_memories: Dict[str, List[Dict]] = {}
        self._memory_counter = 0
    
    def _is_configured(self) -> bool:
        """Check if Supermemory is configured"""
        return (
            self.api_key and 
            self.api_key != "your_supermemory_api_key" and
            len(self.api_key) > 10
        )
    
    def _get_container_tag(self, company_id: str) -> str:
        """Get container tag for a company"""
        return f"sitemind_{company_id}"
    
    # =========================================================================
    # ADD MEMORIES
    # =========================================================================
    
    async def add_memory(
        self,
        company_id: str,
        project_id: str,
        content: str,
        memory_type: str,
        metadata: Dict = None,
        user_id: str = None,
    ) -> Memory:
        """
        Add a memory to the project
        
        Args:
            company_id: Company identifier (for container)
            project_id: Project identifier (for filtering)
            content: The content to remember
            memory_type: Type (decision, query, document, rfi, change_order, photo)
            metadata: Additional structured data
            user_id: Who added this memory
            
        Returns:
            Memory record with ID
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Build enriched content with metadata for better search
        enriched_content = self._build_enriched_content(
            content, memory_type, project_id, metadata, timestamp
        )
        
        # Try Supermemory first
        if self.client:
            try:
                container_tag = self._get_container_tag(company_id)
                
                # Add to Supermemory
                result = self.client.add(
                    content=enriched_content,
                    container_tag=container_tag,
                )
                
                # Handle SDK response object (not dict)
                if hasattr(result, 'id'):
                    memory_id = result.id
                elif hasattr(result, '__dict__'):
                    memory_id = getattr(result, 'id', None) or f"sm_{timestamp}"
                else:
                    memory_id = f"sm_{timestamp}"
                
                logger.info(f"💾 Memory added to Supermemory: {content[:50]}...")
                
                return Memory(
                    id=memory_id,
                    content=content,
                    memory_type=memory_type,
                    project_id=project_id,
                    company_id=company_id,
                    user_id=user_id,
                    metadata=metadata,
                    timestamp=timestamp,
                )
                
            except Exception as e:
                logger.error(f"Supermemory add error: {e}")
        
        # Fallback to local storage
        return self._add_local(company_id, project_id, content, memory_type, metadata, user_id, timestamp)
    
    def _build_enriched_content(
        self,
        content: str,
        memory_type: str,
        project_id: str,
        metadata: Dict,
        timestamp: str,
    ) -> str:
        """Build enriched content with metadata for better search"""
        parts = [
            f"[{memory_type.upper()}]",
            f"[Project: {project_id}]",
            f"[Date: {timestamp[:10]}]",
            "",
            content,
        ]
        
        # Add key metadata to content for search
        if metadata:
            if metadata.get("decision"):
                parts.append(f"\nDecision: {metadata['decision']}")
            if metadata.get("reason"):
                parts.append(f"Reason: {metadata['reason']}")
            if metadata.get("approved_by"):
                parts.append(f"Approved by: {metadata['approved_by']}")
            if metadata.get("old_spec"):
                parts.append(f"Changed from: {metadata['old_spec']}")
            if metadata.get("new_spec"):
                parts.append(f"Changed to: {metadata['new_spec']}")
        
        return "\n".join(parts)
    
    def _add_local(
        self,
        company_id: str,
        project_id: str,
        content: str,
        memory_type: str,
        metadata: Dict,
        user_id: str,
        timestamp: str,
    ) -> Memory:
        """Add to local memory (fallback)"""
        self._memory_counter += 1
        memory_id = f"local_{self._memory_counter}_{timestamp}"
        
        key = f"{company_id}_{project_id}"
        if key not in self._local_memories:
            self._local_memories[key] = []
        
        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            project_id=project_id,
            company_id=company_id,
            user_id=user_id,
            metadata=metadata,
            timestamp=timestamp,
        )
        
        self._local_memories[key].append(memory.to_dict())
        logger.info(f"💾 Memory added locally: {content[:50]}...")
        
        return memory
    
    # =========================================================================
    # SEARCH MEMORIES
    # =========================================================================
    
    async def search(
        self,
        company_id: str,
        query: str,
        project_id: str = None,
        memory_types: List[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Search memories with semantic search
        
        Args:
            company_id: Company to search in
            query: Search query (semantic)
            project_id: Optional project filter
            memory_types: Optional type filter
            limit: Max results
            
        Returns:
            List of matching memories with scores
        """
        # Build search query with filters
        search_query = query
        if project_id:
            search_query = f"[Project: {project_id}] {query}"
        if memory_types:
            type_str = " OR ".join([f"[{t.upper()}]" for t in memory_types])
            search_query = f"({type_str}) {search_query}"
        
        # Try Supermemory
        if self.client:
            try:
                container_tag = self._get_container_tag(company_id)
                
                # Use profile for enriched context
                result = self.client.profile(
                    container_tag=container_tag,
                    q=search_query,
                )
                
                # Handle SDK response object (not dict)
                if hasattr(result, 'memories'):
                    memories = result.memories or []
                elif hasattr(result, '__dict__'):
                    memories = getattr(result, 'memories', []) or []
                else:
                    memories = []
                
                # Parse and filter results
                parsed = []
                for mem in memories[:limit]:
                    # Handle both dict and object responses
                    if hasattr(mem, 'content'):
                        content = mem.content or ""
                        mem_id = getattr(mem, 'id', None)
                        mem_score = getattr(mem, 'score', 0)
                    else:
                        content = mem.get("content", "") if isinstance(mem, dict) else ""
                        mem_id = mem.get("id") if isinstance(mem, dict) else None
                        mem_score = mem.get("score", 0) if isinstance(mem, dict) else 0
                    
                    # Filter by project if specified
                    if project_id and f"[Project: {project_id}]" not in content:
                        continue
                    
                    # Filter by type if specified
                    if memory_types:
                        has_type = any(f"[{t.upper()}]" in content for t in memory_types)
                        if not has_type:
                            continue
                    
                    parsed.append({
                        "id": mem_id,
                        "content": self._extract_clean_content(content),
                        "score": mem_score,
                        "metadata": self._extract_metadata(content),
                    })
                
                logger.info(f"🔍 Supermemory search: '{query[:30]}...' → {len(parsed)} results")
                return parsed[:limit]
                
            except Exception as e:
                logger.error(f"Supermemory search error: {e}")
        
        # Fallback to local search
        return self._search_local(company_id, project_id, query, memory_types, limit)
    
    def _extract_clean_content(self, enriched_content: str) -> str:
        """Extract clean content from enriched format"""
        lines = enriched_content.split("\n")
        # Skip metadata lines (start with [)
        content_lines = [l for l in lines if not l.startswith("[") and l.strip()]
        return "\n".join(content_lines)
    
    def _extract_metadata(self, enriched_content: str) -> Dict:
        """Extract metadata from enriched content"""
        metadata = {}
        lines = enriched_content.split("\n")
        
        for line in lines:
            if line.startswith("[") and "]" in line:
                # Parse [KEY: value] format
                inner = line[1:line.index("]")]
                if ": " in inner:
                    key, value = inner.split(": ", 1)
                    metadata[key.lower()] = value
            elif ": " in line:
                # Parse "Key: value" format
                key, value = line.split(": ", 1)
                metadata[key.lower().replace(" ", "_")] = value
        
        return metadata
    
    def _search_local(
        self,
        company_id: str,
        project_id: str,
        query: str,
        memory_types: List[str],
        limit: int,
    ) -> List[Dict]:
        """Search local memories (fallback)"""
        # Collect all relevant memories
        all_memories = []
        
        for key, memories in self._local_memories.items():
            if not key.startswith(company_id):
                continue
            
            if project_id and not key.endswith(project_id):
                continue
            
            all_memories.extend(memories)
        
        # Score by keyword matching
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored = []
        for mem in all_memories:
            # Filter by type (check 'type', 'memory_type', and nested in metadata)
            mem_type = mem.get("type") or mem.get("memory_type") or mem.get("metadata", {}).get("type")
            if memory_types and mem_type not in memory_types:
                continue
            
            content = mem.get("content", "").lower()
            
            # Also search in metadata for better matching
            metadata = mem.get("metadata", {})
            metadata_str = " ".join(str(v) for v in metadata.values() if v).lower()
            searchable = f"{content} {metadata_str}"
            
            # Score: count matching words
            score = sum(1 for word in query_words if word in searchable)
            
            # Boost score for exact phrase match
            if query_lower in searchable:
                score += 2
            
            if score > 0:
                scored.append({
                    "id": mem.get("id"),
                    "content": mem.get("content"),
                    "score": score / len(query_words),  # Normalize
                    "metadata": metadata,
                    "type": mem_type,
                })
        
        # Sort by score
        scored.sort(key=lambda x: -x["score"])
        
        logger.info(f"🔍 Local search: '{query[:30]}...' → {len(scored[:limit])} results")
        return scored[:limit]
    
    # =========================================================================
    # GET CONTEXT FOR AI
    # =========================================================================
    
    async def get_context(
        self,
        company_id: str,
        project_id: str,
        query: str,
        include_types: List[str] = None,
    ) -> List[Dict]:
        """
        Get relevant context for AI response
        
        Combines:
        1. Semantic search for query
        2. Recent decisions/changes
        3. Relevant RFIs
        
        Returns context optimized for Gemini prompt injection
        """
        context = []
        
        # 1. Main search
        results = await self.search(
            company_id=company_id,
            query=query,
            project_id=project_id,
            memory_types=include_types,
            limit=5,
        )
        context.extend(results)
        
        # 2. Recent decisions (always relevant)
        if not include_types or "decision" in include_types:
            decisions = await self.search(
                company_id=company_id,
                query="decision change approved",
                project_id=project_id,
                memory_types=["decision", "change_order"],
                limit=3,
            )
            
            # Add if not duplicate
            existing_ids = {c.get("id") for c in context}
            for d in decisions:
                if d.get("id") not in existing_ids:
                    context.append(d)
        
        # Limit total context
        return context[:7]
    
    def format_context_for_prompt(self, context: List[Dict]) -> str:
        """Format context for Gemini prompt"""
        if not context:
            return ""
        
        lines = ["**Relevant Project Context:**", ""]
        
        for i, item in enumerate(context, 1):
            content = item.get("content", "")[:300]
            metadata = item.get("metadata", {})
            
            lines.append(f"{i}. {content}")
            
            if metadata.get("decision"):
                lines.append(f"   Decision: {metadata['decision']}")
            if metadata.get("approved_by"):
                lines.append(f"   Approved by: {metadata['approved_by']}")
            if metadata.get("date"):
                lines.append(f"   Date: {metadata['date']}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    # =========================================================================
    # SPECIALIZED ADD METHODS
    # =========================================================================
    
    async def add_decision(
        self,
        company_id: str,
        project_id: str,
        decision: str,
        reason: str = None,
        approved_by: str = None,
        affected_area: str = None,
        user_id: str = None,
    ) -> Memory:
        """Add a project decision"""
        content = f"Decision: {decision}"
        if reason:
            content += f"\nReason: {reason}"
        if approved_by:
            content += f"\nApproved by: {approved_by}"
        if affected_area:
            content += f"\nAffected area: {affected_area}"
        
        return await self.add_memory(
            company_id=company_id,
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
        company_id: str,
        project_id: str,
        description: str,
        old_spec: str,
        new_spec: str,
        reason: str = None,
        approved_by: str = None,
        user_id: str = None,
    ) -> Memory:
        """Add a change order"""
        content = f"Change Order: {description}\n"
        content += f"Changed from: {old_spec}\n"
        content += f"Changed to: {new_spec}"
        if reason:
            content += f"\nReason: {reason}"
        if approved_by:
            content += f"\nApproved by: {approved_by}"
        
        return await self.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=content,
            memory_type="change_order",
            metadata={
                "description": description,
                "old_spec": old_spec,
                "new_spec": new_spec,
                "reason": reason,
                "approved_by": approved_by,
            },
            user_id=user_id,
        )
    
    async def add_rfi(
        self,
        company_id: str,
        project_id: str,
        question: str,
        answer: str = None,
        asked_by: str = None,
        answered_by: str = None,
        rfi_number: str = None,
        user_id: str = None,
    ) -> Memory:
        """Add an RFI (Request for Information)"""
        content = f"RFI"
        if rfi_number:
            content += f" #{rfi_number}"
        content += f": {question}"
        
        if answer:
            content += f"\nAnswer: {answer}"
            if answered_by:
                content += f"\n(Answered by {answered_by})"
        
        return await self.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=content,
            memory_type="rfi",
            metadata={
                "question": question,
                "answer": answer,
                "asked_by": asked_by,
                "answered_by": answered_by,
                "rfi_number": rfi_number,
                "status": "answered" if answer else "pending",
            },
            user_id=user_id,
        )
    
    async def add_query(
        self,
        company_id: str,
        project_id: str,
        question: str,
        answer: str,
        user_id: str = None,
    ) -> Memory:
        """Add a Q&A from WhatsApp"""
        content = f"Q: {question}\nA: {answer}"
        
        return await self.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=content,
            memory_type="query",
            metadata={
                "question": question,
                "answer": answer[:500],  # Truncate long answers
            },
            user_id=user_id,
        )
    
    async def add_document(
        self,
        company_id: str,
        project_id: str,
        document_name: str,
        document_type: str,
        extracted_text: str,
        file_path: str = None,
        user_id: str = None,
    ) -> Memory:
        """Add document content to memory"""
        content = f"Document: {document_name}\n"
        content += f"Type: {document_type}\n"
        content += f"Content:\n{extracted_text[:2000]}"  # Limit for memory efficiency
        
        return await self.add_memory(
            company_id=company_id,
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
    
    async def add_photo_analysis(
        self,
        company_id: str,
        project_id: str,
        caption: str,
        analysis: str,
        file_path: str = None,
        photo_type: str = None,
        user_id: str = None,
    ) -> Memory:
        """Add photo analysis to memory"""
        content = f"Photo Analysis"
        if caption:
            content += f": {caption}"
        content += f"\n\n{analysis}"
        
        return await self.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=content,
            memory_type="photo",
            metadata={
                "caption": caption,
                "analysis": analysis[:500],
                "file_path": file_path,
                "photo_type": photo_type,
            },
            user_id=user_id,
        )
    
    # =========================================================================
    # AUDIT TRAIL
    # =========================================================================
    
    async def get_audit_trail(
        self,
        company_id: str,
        project_id: str,
        topic: str = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Get audit trail for legal/documentation purposes
        
        Returns chronological list of decisions and changes
        """
        results = await self.search(
            company_id=company_id,
            query=topic or "decision change order approval",
            project_id=project_id,
            memory_types=["decision", "change_order", "rfi"],
            limit=limit,
        )
        
        return results
    
    def format_audit_trail(self, trail: List[Dict]) -> str:
        """Format audit trail for export/display"""
        lines = [
            "=" * 60,
            "AUDIT TRAIL",
            "=" * 60,
            "",
        ]
        
        for i, item in enumerate(trail, 1):
            metadata = item.get("metadata", {})
            lines.append(f"--- Record {i} ---")
            lines.append(f"Date: {metadata.get('date', 'Unknown')}")
            lines.append(f"Type: {metadata.get('type', 'Unknown').upper()}")
            lines.append(f"Content: {item.get('content', '')}")
            
            if metadata.get("approved_by"):
                lines.append(f"Approved by: {metadata['approved_by']}")
            if metadata.get("reason"):
                lines.append(f"Reason: {metadata['reason']}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_local_stats(self, company_id: str, project_id: str = None) -> Dict[str, int]:
        """Get memory stats (local only - for billing estimates)"""
        stats = {
            "total": 0,
            "decisions": 0,
            "change_orders": 0,
            "rfis": 0,
            "queries": 0,
            "documents": 0,
            "photos": 0,
        }
        
        for key, memories in self._local_memories.items():
            if not key.startswith(company_id):
                continue
            if project_id and not key.endswith(project_id):
                continue
            
            for mem in memories:
                stats["total"] += 1
                mem_type = mem.get("memory_type", "other")
                if mem_type in stats:
                    stats[mem_type] += 1
        
        return stats


# Singleton instance
memory_service = MemoryService()
