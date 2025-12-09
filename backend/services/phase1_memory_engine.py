"""
PHASE 1: PROJECT MEMORY ENGINE
==============================

Turn WhatsApp + drawings + messages into structured, searchable, unified project memory.

CAPABILITIES (100% Gemini 3.0):
- WhatsApp ingestion (text, PDFs, voice transcripts)
- Drawing upload + text extraction
- RFI detection + management
- Decision logging
- Daily project summary
- Ask-me-anything search

NO COMPUTER VISION. JUST TEXT + EMBEDDINGS + LLM.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from services.memory_service import memory_service
from services.gemini_service import gemini_service
from utils.logger import logger


@dataclass
class RFI:
    id: str
    title: str
    question: str
    raised_by: str
    raised_at: datetime
    assigned_to: str = None
    status: str = "open"  # open, responded, closed
    response: str = None
    responded_by: str = None
    responded_at: datetime = None
    linked_messages: List[str] = field(default_factory=list)
    linked_drawing: str = None


@dataclass
class Decision:
    id: str
    description: str
    approved_by: str
    approved_at: datetime
    context: str = None
    linked_messages: List[str] = field(default_factory=list)
    linked_drawing: str = None


@dataclass
class DrawingInfo:
    name: str
    sheet_number: str = None
    title: str = None
    revision: str = None
    uploaded_at: datetime = None
    uploaded_by: str = None
    notes: List[str] = field(default_factory=list)
    specs: Dict[str, Any] = field(default_factory=dict)
    materials: List[str] = field(default_factory=list)


class ProjectMemoryEngine:
    """
    Phase 1: The foundation of SiteMind
    
    - Ingests all project data
    - Extracts structured information
    - Makes everything searchable
    """
    
    def __init__(self):
        self._rfis: Dict[str, List[RFI]] = {}
        self._decisions: Dict[str, List[Decision]] = {}
        self._drawings: Dict[str, List[DrawingInfo]] = {}
        self._messages: Dict[str, List[Dict]] = {}
    
    # =========================================================================
    # 1. MESSAGE CLASSIFICATION
    # =========================================================================
    
    async def classify_message(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Classify incoming message using Gemini
        
        Categories:
        - rfi: Request for information
        - decision: Approval or decision
        - issue: Problem reported
        - update: Progress update
        - question: General query
        - general: Regular communication
        """
        
        prompt = f"""Classify this construction project message.

MESSAGE: "{message}"
SENDER: {sender}

Return JSON only:
{{
  "category": "rfi|decision|issue|update|question|general",
  "confidence": 0.0-1.0,
  "extracted": {{
    "title": "brief title if applicable",
    "assigned_to": "person mentioned if any",
    "severity": "high|medium|low if issue",
    "work_type": "type of work if update",
    "location": "location mentioned if any"
  }}
}}"""

        try:
            response = await gemini_service._generate(prompt)
            # Extract JSON
            result = self._extract_json(response)
            return result or {"category": "general", "confidence": 0.5, "extracted": {}}
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {"category": "general", "confidence": 0.0, "extracted": {}}
    
    async def process_message(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Process and store a message
        """
        key = f"{company_id}_{project_id}"
        
        # Classify
        classification = await self.classify_message(message, sender, company_id, project_id)
        
        # Store in memory
        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=f"[{sender}]: {message}",
            memory_type=classification["category"],
            metadata={
                "sender": sender,
                "classification": classification,
                "timestamp": datetime.utcnow().isoformat(),
            },
            user_id=sender,
        )
        
        # Track locally
        if key not in self._messages:
            self._messages[key] = []
        
        self._messages[key].append({
            "message": message,
            "sender": sender,
            "classification": classification,
            "timestamp": datetime.utcnow(),
        })
        
        # Auto-create RFI if detected
        if classification["category"] == "rfi":
            await self.create_rfi_from_message(
                message=message,
                sender=sender,
                company_id=company_id,
                project_id=project_id,
                extracted=classification.get("extracted", {}),
            )
        
        # Auto-log decision if detected
        if classification["category"] == "decision":
            await self.log_decision_from_message(
                message=message,
                sender=sender,
                company_id=company_id,
                project_id=project_id,
                extracted=classification.get("extracted", {}),
            )
        
        return classification
    
    # =========================================================================
    # 2. DRAWING STORAGE (HONEST - We store, not analyze)
    # =========================================================================
    
    async def extract_drawing_info(
        self,
        document_text: str,
        file_name: str,
        company_id: str,
        project_id: str,
        uploaded_by: str,
    ) -> DrawingInfo:
        """
        Store drawing metadata
        
        HONEST: We can only extract info from the FILENAME
        - Try to parse sheet number (STR-07, ARC-12)
        - Try to parse revision (R1, R2, Rev-A)
        - Store upload metadata
        
        We CANNOT read the actual drawing content.
        """
        import re
        
        # Extract from filename only
        sheet_number = None
        revision = None
        
        # Try to extract sheet number (e.g., STR-07, ARC-12, MEP-03)
        sheet_match = re.search(r'([A-Z]{2,4}[-_]?\d{1,3})', file_name.upper())
        if sheet_match:
            sheet_number = sheet_match.group(1)
        
        # Try to extract revision (e.g., R1, R2, Rev-A, -R3)
        rev_match = re.search(r'[-_]?R(?:ev)?[-_]?(\d+|[A-Z])', file_name, re.IGNORECASE)
        if rev_match:
            revision = f"R{rev_match.group(1).upper()}"
        
        drawing = DrawingInfo(
            name=file_name,
            sheet_number=sheet_number,
            title=None,  # We can't know this without reading
            revision=revision,
            uploaded_at=datetime.utcnow(),
            uploaded_by=uploaded_by,
            notes=[],
            specs={},
            materials=[],
        )
        
        # Store
        key = f"{company_id}_{project_id}"
        if key not in self._drawings:
            self._drawings[key] = []
        self._drawings[key].append(drawing)
        
        # Store in memory for search
        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=f"Drawing uploaded: {file_name} (Sheet: {sheet_number or 'Unknown'}, Rev: {revision or 'Unknown'}) by {uploaded_by}",
            memory_type="drawing",
            metadata={
                "file_name": file_name,
                "sheet_number": sheet_number,
                "revision": revision,
                "uploaded_by": uploaded_by,
            },
            user_id=uploaded_by,
        )
        
        logger.info(f"📐 Drawing stored: {file_name}")
        
        return drawing
    
    # =========================================================================
    # 3. RFI MANAGEMENT
    # =========================================================================
    
    async def create_rfi_from_message(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
        extracted: Dict = None,
    ) -> RFI:
        """Auto-create RFI from detected message"""
        
        key = f"{company_id}_{project_id}"
        if key not in self._rfis:
            self._rfis[key] = []
        
        rfi = RFI(
            id=f"RFI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=extracted.get("title", message[:50]),
            question=message,
            raised_by=sender,
            raised_at=datetime.utcnow(),
            assigned_to=extracted.get("assigned_to"),
            linked_messages=[message],
        )
        
        self._rfis[key].append(rfi)
        
        # Store in memory
        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=f"RFI: {rfi.title} - {rfi.question} (Raised by: {sender}, Status: {rfi.status})",
            memory_type="rfi",
            metadata={"rfi_id": rfi.id, "status": rfi.status},
            user_id=sender,
        )
        
        logger.info(f"📋 RFI created: {rfi.id}")
        return rfi
    
    async def create_rfi(
        self,
        title: str,
        question: str,
        raised_by: str,
        company_id: str,
        project_id: str,
        assigned_to: str = None,
    ) -> RFI:
        """Manually create an RFI"""
        
        key = f"{company_id}_{project_id}"
        if key not in self._rfis:
            self._rfis[key] = []
        
        rfi = RFI(
            id=f"RFI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=title,
            question=question,
            raised_by=raised_by,
            raised_at=datetime.utcnow(),
            assigned_to=assigned_to,
        )
        
        self._rfis[key].append(rfi)
        
        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=f"RFI: {title} - {question} (Raised by: {raised_by}, Assigned to: {assigned_to or 'Unassigned'})",
            memory_type="rfi",
            metadata={"rfi_id": rfi.id, "status": "open"},
            user_id=raised_by,
        )
        
        return rfi
    
    def get_open_rfis(self, company_id: str, project_id: str) -> List[RFI]:
        """Get all open RFIs"""
        key = f"{company_id}_{project_id}"
        if key not in self._rfis:
            return []
        return [r for r in self._rfis[key] if r.status == "open"]
    
    def get_overdue_rfis(self, company_id: str, project_id: str, days: int = 3) -> List[RFI]:
        """Get overdue RFIs"""
        key = f"{company_id}_{project_id}"
        if key not in self._rfis:
            return []
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [r for r in self._rfis[key] if r.status == "open" and r.raised_at < cutoff]
    
    async def respond_to_rfi(
        self,
        rfi_id: str,
        response: str,
        responded_by: str,
        company_id: str,
        project_id: str,
    ) -> Optional[RFI]:
        """Respond to an RFI"""
        key = f"{company_id}_{project_id}"
        if key not in self._rfis:
            return None
        
        for rfi in self._rfis[key]:
            if rfi.id == rfi_id:
                rfi.response = response
                rfi.responded_by = responded_by
                rfi.responded_at = datetime.utcnow()
                rfi.status = "responded"
                
                await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=f"RFI Response: {rfi.title} - Response: {response} (By: {responded_by})",
                    memory_type="rfi_response",
                    metadata={"rfi_id": rfi_id, "status": "responded"},
                    user_id=responded_by,
                )
                return rfi
        return None
    
    # =========================================================================
    # 4. DECISION LOGGING
    # =========================================================================
    
    async def log_decision_from_message(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
        extracted: Dict = None,
    ) -> Decision:
        """Auto-log decision from detected message"""
        
        key = f"{company_id}_{project_id}"
        if key not in self._decisions:
            self._decisions[key] = []
        
        decision = Decision(
            id=f"DEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=message,
            approved_by=sender,
            approved_at=datetime.utcnow(),
            linked_messages=[message],
        )
        
        self._decisions[key].append(decision)
        
        await memory_service.add_decision(
            company_id=company_id,
            project_id=project_id,
            decision=message,
            approved_by=sender,
            user_id=sender,
        )
        
        logger.info(f"✅ Decision logged: {decision.id}")
        return decision
    
    async def log_decision(
        self,
        description: str,
        approved_by: str,
        company_id: str,
        project_id: str,
        context: str = None,
    ) -> Decision:
        """Manually log a decision"""
        
        key = f"{company_id}_{project_id}"
        if key not in self._decisions:
            self._decisions[key] = []
        
        decision = Decision(
            id=f"DEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=description,
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            context=context,
        )
        
        self._decisions[key].append(decision)
        
        await memory_service.add_decision(
            company_id=company_id,
            project_id=project_id,
            decision=description,
            approved_by=approved_by,
            user_id=approved_by,
        )
        
        return decision
    
    def get_decisions(self, company_id: str, project_id: str, limit: int = 50) -> List[Decision]:
        """Get recent decisions"""
        key = f"{company_id}_{project_id}"
        if key not in self._decisions:
            return []
        
        decisions = sorted(self._decisions[key], key=lambda x: x.approved_at, reverse=True)
        return decisions[:limit]
    
    # =========================================================================
    # 5. DAILY SUMMARY
    # =========================================================================
    
    async def generate_daily_summary(
        self,
        company_id: str,
        project_id: str,
    ) -> str:
        """
        Generate daily project summary using Gemini
        
        Summarizes:
        - Progress updates
        - Issues reported
        - Pending approvals
        - RFIs
        - Delays
        - Materials
        """
        
        # Get today's context
        context = await memory_service.get_context(
            company_id=company_id,
            project_id=project_id,
            query="today's updates progress issues decisions materials delays",
        )
        
        if not context:
            return """📊 *Daily Summary*

No activity recorded today.

_Send updates, decisions, or issues to SiteMind to start tracking._"""
        
        # Format context
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context[:20]
        ])
        
        prompt = f"""Generate a daily project summary from this activity.

TODAY'S ACTIVITY:
{context_text}

FORMAT:
📊 *Daily Summary - [Date]*

*Progress:*
• [What work was done]

*Issues:*
• [Problems reported]

*Decisions Made:*
• [Approvals and decisions]

*Pending:*
• [Open RFIs, awaiting responses]

*Risks:*
• [Potential delays or problems]

Be concise. Use bullet points. Focus on actionable items."""

        try:
            summary = await gemini_service._generate(prompt)
            return summary
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return f"📊 *Daily Summary*\n\n{len(context)} items recorded today."
    
    # =========================================================================
    # 6. ASK-ME-ANYTHING SEARCH
    # =========================================================================
    
    async def search(
        self,
        query: str,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Search project memory and answer questions
        
        Examples:
        - "Show all messages about plumbing on Tower A"
        - "Find the screenshot of STR-11 from last week"
        - "Show all updates about waterproofing"
        """
        
        # Search memory
        results = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=query,
            limit=15,
        )
        
        if not results:
            return {
                "answer": f"No results found for: {query}\n\n_Try a different search term or upload more project data._",
                "results": [],
            }
        
        # Format results for LLM
        results_text = "\n".join([
            f"{i+1}. {item.get('content', str(item))[:300]}"
            for i, item in enumerate(results[:10])
        ])
        
        # Use LLM to synthesize answer
        prompt = f"""Answer this question using the search results.

QUESTION: {query}

SEARCH RESULTS:
{results_text}

INSTRUCTIONS:
1. Answer the question directly
2. Cite which result(s) you used
3. If the answer isn't in the results, say so
4. Be concise and practical"""

        try:
            answer = await gemini_service._generate(prompt)
            return {
                "answer": answer,
                "results": results[:10],
                "count": len(results),
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "answer": f"Found {len(results)} results. Here are the top matches:",
                "results": results[:5],
            }
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text"""
        import re
        try:
            # Try to find JSON block - handles nested braces
            # Find the first { and last }
            start = text.find('{')
            if start == -1:
                return None
            
            # Count braces to find matching }
            depth = 0
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = text[start:i+1]
                        return json.loads(json_str)
            return None
        except Exception as e:
            logger.debug(f"JSON extraction failed: {e}")
            return None
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_stats(self, company_id: str, project_id: str) -> Dict[str, Any]:
        """Get project stats"""
        key = f"{company_id}_{project_id}"
        
        rfis = self._rfis.get(key, [])
        decisions = self._decisions.get(key, [])
        drawings = self._drawings.get(key, [])
        messages = self._messages.get(key, [])
        
        return {
            "total_messages": len(messages),
            "total_rfis": len(rfis),
            "open_rfis": len([r for r in rfis if r.status == "open"]),
            "overdue_rfis": len(self.get_overdue_rfis(company_id, project_id)),
            "total_decisions": len(decisions),
            "total_drawings": len(drawings),
        }


# Singleton
memory_engine = ProjectMemoryEngine()

