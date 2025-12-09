"""
SiteMind CORE - Boringly Reliable, Not Magical
===============================================

POSITIONING:
"Your Senior Project Engineer sitting inside WhatsApp"

WHAT WE DO (reliably):
1. Answer drawing questions with EXACT citations
2. Track decisions and approvals
3. Manage RFIs
4. Remember everything
5. Summarize WhatsApp chaos
6. Track drawing revisions

WHAT WE DON'T DO (on purpose):
- "AI detects rebar mismatch from photo" ❌
- "AI automatically catches all mistakes" ❌
- Overpromise and underdeliver ❌

PHILOSOPHY:
Predictable > Magical
Reliable > Impressive
Cited > Hallucinated
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from services.memory_service import memory_service
from services.gemini_service import gemini_service
from utils.logger import logger


class SiteMindCore:
    """
    The Reliable Project Brain
    
    Focused on:
    - Drawing Q&A with citations
    - Decision logging
    - RFI tracking
    - Revision intelligence
    - Daily summaries
    
    NOT focused on:
    - Risky computer vision claims
    - "Magical" AI detection
    """
    
    def __init__(self):
        self.system_prompt = """You are SiteMind, a reliable project assistant for construction sites.

YOUR ROLE:
You are like a senior project engineer who:
- Knows every drawing that was uploaded
- Remembers every decision that was made
- Tracks all RFIs and their status
- Can find any information instantly

YOUR RULES (CRITICAL):
1. ONLY answer based on information you have in context
2. ALWAYS cite the source: "From STR-07, Rev R2, Page 14"
3. If information is NOT in context, say: "I don't have this information. Please upload the relevant drawing."
4. NEVER make up specifications or details
5. NEVER claim to "detect" things from photos - just log what the user tells you
6. Be concise and practical - site engineers need quick answers

YOUR CAPABILITIES:
- Answer questions about drawings/specs WITH citations
- Log decisions and approvals
- Track RFIs
- Remember project history
- Summarize conversations

YOUR LIMITATIONS (be honest about these):
- You can only answer based on uploaded documents
- You cannot "detect" issues from photos automatically
- You are not a replacement for QA/QC

RESPONSE FORMAT:
- Keep answers short and practical
- Always include source citation
- If uncertain, say so clearly"""

    async def process_message(
        self,
        message: str,
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str = "User",
        message_type: str = "text",
        media_caption: str = None,
    ) -> Dict[str, Any]:
        """
        Process message with reliability over magic
        """
        
        logger.info(f"📥 Processing: {message[:50]}... from {user_name}")
        
        # Get relevant context
        context = await self._get_context(company_id, project_id, message)
        
        # Determine intent and respond
        result = await self._process_with_context(
            message=message,
            context=context,
            company_id=company_id,
            project_id=project_id,
            user_id=user_id,
            user_name=user_name,
        )
        
        # Store interaction
        await self._store_interaction(
            company_id=company_id,
            project_id=project_id,
            user_id=user_id,
            user_name=user_name,
            message=message,
            response=result.get("answer", ""),
        )
        
        return result

    async def _get_context(
        self,
        company_id: str,
        project_id: str,
        query: str,
    ) -> List[Dict]:
        """Get relevant context from memory"""
        return await memory_service.get_context(
            company_id=company_id,
            project_id=project_id,
            query=query,
        )

    async def _process_with_context(
        self,
        message: str,
        context: List[Dict],
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str,
    ) -> Dict[str, Any]:
        """
        Process with AI - focused on reliability
        """
        
        # Format context clearly
        context_text = self._format_context(context)
        
        prompt = f"""{self.system_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVAILABLE PROJECT INFORMATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context_text if context_text else "(No documents uploaded yet for this project)"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER MESSAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From: {user_name}
Message: {message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPOND:
- If this is a QUESTION: Answer using ONLY the information above. Cite the source.
- If this is INFORMATION/UPDATE: Acknowledge and confirm you've noted it.
- If this is a DECISION: Confirm the decision is logged with who made it and when.
- If information is NOT available: Say so clearly and ask for the relevant document.

Be concise. Be reliable. Always cite sources."""

        try:
            response = await gemini_service._generate(prompt)
            
            # Check if this is something to store
            store_type = self._detect_store_type(message)
            
            return {
                "answer": response,
                "context_used": len(context),
                "store_type": store_type,
                "status": "success",
            }
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {
                "answer": "I received your message but had trouble processing it. Please try again.",
                "status": "error",
                "error": str(e),
            }

    def _format_context(self, context: List[Dict]) -> str:
        """Format context for the prompt"""
        if not context:
            return ""
        
        lines = []
        for i, item in enumerate(context[:15], 1):  # Max 15 items
            content = item.get("content", str(item))
            if len(content) > 400:
                content = content[:400] + "..."
            
            # Extract source info if available
            source = ""
            if "source" in str(item).lower():
                source = " [has source]"
            
            lines.append(f"{i}. {content}{source}")
        
        return "\n\n".join(lines)

    def _detect_store_type(self, message: str) -> Optional[str]:
        """
        Simple detection of what type of info this is
        NOT for making decisions, just for categorization
        """
        message_lower = message.lower()
        
        # Decision keywords
        if any(word in message_lower for word in ["approved", "decided", "confirmed", "agreed", "finalized"]):
            return "decision"
        
        # RFI keywords
        if any(word in message_lower for word in ["rfi", "request for", "clarification needed", "query to"]):
            return "rfi"
        
        # Issue keywords
        if any(word in message_lower for word in ["issue", "problem", "delay", "stuck", "pending"]):
            return "issue"
        
        # Drawing/spec keywords
        if any(word in message_lower for word in ["drawing", "revision", "rev ", "r1", "r2", "r3", "uploaded"]):
            return "drawing"
        
        return "general"

    async def _store_interaction(
        self,
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str,
        message: str,
        response: str,
    ):
        """Store the interaction in memory"""
        
        # Store the Q&A
        await memory_service.add_query(
            company_id=company_id,
            project_id=project_id,
            question=message,
            answer=response[:500],
            user_id=user_id,
        )

    # =========================================================================
    # SPECIFIC FEATURES
    # =========================================================================

    async def log_decision(
        self,
        company_id: str,
        project_id: str,
        decision: str,
        approved_by: str,
        user_id: str,
        context: str = None,
    ) -> str:
        """
        Log a decision with full traceability
        """
        timestamp = datetime.utcnow().strftime("%d-%b-%Y %H:%M")
        
        decision_record = f"""DECISION LOGGED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Decision: {decision}
Approved by: {approved_by}
Date/Time: {timestamp}
{f"Context: {context}" if context else ""}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        await memory_service.add_decision(
            company_id=company_id,
            project_id=project_id,
            decision=decision,
            approved_by=approved_by,
            user_id=user_id,
        )
        
        return f"""✅ *Decision Logged*

{decision}

📋 Approved by: {approved_by}
🕐 Time: {timestamp}

_This decision is now part of the project record._"""

    async def log_rfi(
        self,
        company_id: str,
        project_id: str,
        rfi_description: str,
        raised_by: str,
        assigned_to: str,
        user_id: str,
        due_date: str = None,
    ) -> str:
        """
        Log an RFI
        """
        timestamp = datetime.utcnow().strftime("%d-%b-%Y")
        rfi_id = f"RFI-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        
        rfi_record = f"""RFI: {rfi_description}
ID: {rfi_id}
Raised by: {raised_by}
Assigned to: {assigned_to}
Date: {timestamp}
Due: {due_date or 'Not specified'}
Status: OPEN"""

        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=rfi_record,
            memory_type="rfi",
            metadata={
                "rfi_id": rfi_id,
                "status": "open",
                "assigned_to": assigned_to,
                "raised_by": raised_by,
            },
            user_id=user_id,
        )
        
        return f"""📋 *RFI Logged*

*{rfi_id}*
{rfi_description}

👤 Raised by: {raised_by}
👤 Assigned to: {assigned_to}
📅 Due: {due_date or 'Not specified'}
🔴 Status: OPEN

_SiteMind will track this RFI._"""

    async def log_drawing(
        self,
        company_id: str,
        project_id: str,
        drawing_name: str,
        revision: str,
        uploaded_by: str,
        user_id: str,
        changes: str = None,
    ) -> str:
        """
        Log a drawing upload with revision tracking
        """
        timestamp = datetime.utcnow().strftime("%d-%b-%Y %H:%M")
        
        # Check for previous revisions
        existing = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=f"drawing {drawing_name}",
            limit=5,
        )
        
        previous_revisions = []
        for item in existing:
            content = item.get("content", "")
            if drawing_name.lower() in content.lower() and "revision" in content.lower():
                previous_revisions.append(content[:100])
        
        drawing_record = f"""DRAWING: {drawing_name}
Revision: {revision}
Uploaded by: {uploaded_by}
Date: {timestamp}
Changes: {changes or 'Not specified'}"""

        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=drawing_record,
            memory_type="drawing",
            metadata={
                "drawing_name": drawing_name,
                "revision": revision,
                "uploaded_by": uploaded_by,
            },
            user_id=user_id,
        )
        
        response = f"""📐 *Drawing Logged*

*{drawing_name}* - Revision {revision}

👤 Uploaded by: {uploaded_by}
📅 Date: {timestamp}
{f"📝 Changes: {changes}" if changes else ""}"""

        if previous_revisions:
            response += f"""

⚠️ *Previous Revisions Found:*
This drawing has {len(previous_revisions)} previous version(s) in the system."""
        
        return response

    async def get_daily_summary(
        self,
        company_id: str,
        project_id: str,
    ) -> str:
        """
        Generate a clean daily summary
        """
        
        # Get recent activity
        context = await memory_service.get_context(
            company_id=company_id,
            project_id=project_id,
            query="today's updates decisions issues",
        )
        
        if not context:
            return """📊 *Daily Summary*

No activity recorded today.

_Send updates, decisions, or issues to SiteMind to track them._"""
        
        # Let AI summarize
        prompt = f"""Summarize this project activity into a clean daily summary.

ACTIVITY:
{self._format_context(context[:10])}

FORMAT YOUR RESPONSE AS:
📊 *Daily Summary*

*Decisions Made:*
- [list any decisions]

*Issues Reported:*
- [list any issues]

*RFIs:*
- [list any RFIs and their status]

*Drawings Updated:*
- [list any drawing changes]

*Pending Items:*
- [list anything that needs attention]

Keep it concise and actionable."""

        try:
            summary = await gemini_service._generate(prompt)
            return summary
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return f"📊 *Daily Summary*\n\n{len(context)} items recorded today.\n\n_Ask me specific questions to get details._"

    async def check_drawing_revision(
        self,
        company_id: str,
        project_id: str,
        drawing_name: str,
    ) -> str:
        """
        Check latest revision of a drawing
        """
        
        results = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=f"drawing {drawing_name} revision",
            limit=10,
        )
        
        if not results:
            return f"""📐 *Drawing Check: {drawing_name}*

❌ No records found for this drawing.

_Upload the drawing to SiteMind to start tracking revisions._"""
        
        # Parse revisions from results
        prompt = f"""From these records, extract the drawing revision history:

RECORDS:
{self._format_context(results)}

RESPOND WITH:
📐 *{drawing_name} - Revision History*

Latest: [revision number]
Uploaded: [date]
By: [person]

Previous versions:
- [list previous revisions if any]

If you can't find clear revision info, say so."""

        try:
            response = await gemini_service._generate(prompt)
            return response
        except:
            return f"""📐 *Drawing Check: {drawing_name}*

Found {len(results)} record(s) related to this drawing.

_Ask me a specific question about this drawing._"""


# Singleton
sitemind_core = SiteMindCore()
