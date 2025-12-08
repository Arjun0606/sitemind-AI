"""
SiteMind CORE - AI-First, Citations Always
============================================

CORE PRINCIPLES:
1. NO pattern matching - Gemini understands everything
2. EVERY response has citations - "As discussed on Dec 2 by Rajesh..."
3. INFO DUMP works - Send anything, it becomes searchable knowledge
4. AI reasons through problems - Not just retrieval, actual thinking

HOW IT WORKS:
1. User sends ANYTHING (text, photo, document, voice note transcript)
2. Supermemory stores it immediately (info dump)
3. Supermemory retrieves ALL relevant context
4. Gemini REASONS with context and gives answer WITH CITATIONS
5. Response shows WHERE the info came from

THE MAGIC:
- Send "column size is 450mm" → Stored forever
- Later ask "column size?" → "450mm (shared by Rajesh on Dec 8)"
- Send photo → AI analyzes + checks against stored specs
- Every suggestion has reasoning + sources
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from utils.logger import logger
from services.memory_service import memory_service
from services.gemini_service import gemini_service


class SiteMindCore:
    """
    AI-First Construction Assistant
    
    NO pattern matching.
    ALL AI understanding.
    ALWAYS cite sources.
    """
    
    def __init__(self):
        pass
    
    async def process_message(
        self,
        message: str,
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str = "",
        user_role: str = "site_engineer",
        photo_url: str = None,
        photo_data: bytes = None,
    ) -> Dict[str, Any]:
        """
        Process ANY message with AI understanding and citations
        
        This is the ONLY entry point. Handles everything:
        - Questions → Answered with citations
        - Information → Stored and acknowledged  
        - Photos → Analyzed against project context
        - Issues → Flagged with recommendations
        """
        
        logger.info(f"📩 Message from {user_name or user_id}: {message[:50]}...")
        
        # =====================================================================
        # STEP 1: STORE IMMEDIATELY (Info Dump)
        # Everything shared becomes searchable knowledge
        # =====================================================================
        
        memory_id = await self._store_incoming(
            company_id=company_id,
            project_id=project_id,
            user_id=user_id,
            user_name=user_name,
            message=message,
            has_photo=photo_data is not None,
        )
        
        # =====================================================================
        # STEP 2: RETRIEVE ALL RELEVANT CONTEXT
        # Supermemory semantic search
        # =====================================================================
        
        context = await self._get_context(
            company_id=company_id,
            project_id=project_id,
            query=message,
        )
        
        logger.info(f"🔍 Retrieved {len(context)} relevant memories")
        
        # =====================================================================
        # STEP 3: AI UNDERSTANDS AND RESPONDS WITH CITATIONS
        # Gemini does ALL the thinking
        # =====================================================================
        
        if photo_data:
            response = await self._process_with_photo(
                message=message,
                photo_data=photo_data,
                context=context,
                user_name=user_name,
                project_id=project_id,
            )
        else:
            response = await self._process_with_ai(
                message=message,
                context=context,
                user_name=user_name,
                project_id=project_id,
            )
        
        # =====================================================================
        # STEP 4: STORE THE RESPONSE TOO
        # So future queries can reference this conversation
        # =====================================================================
        
        await self._store_response(
            company_id=company_id,
            project_id=project_id,
            user_id=user_id,
            user_name=user_name,
            question=message,
            answer=response["answer"],
        )
        
        return response
    
    # =========================================================================
    # AI PROCESSING - Gemini does ALL understanding
    # =========================================================================
    
    async def _process_with_ai(
        self,
        message: str,
        context: List[Dict],
        user_name: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Let AI understand the message and respond with citations
        
        NO pattern matching. AI figures out:
        - Is this a question? → Answer with sources
        - Is this information? → Acknowledge and confirm stored
        - Is this an issue? → Provide recommendations with reasoning
        - Is this a decision? → Confirm and note for records
        """
        
        # Format context with metadata for citations
        context_with_sources = self._format_context_for_citations(context)
        
        # THE MASTER PROMPT - AI does everything
        prompt = f"""You are SiteMind, an AI construction expert assistant.

YOUR JOB:
1. Understand what the user is saying/asking
2. Use the PROJECT CONTEXT below to give accurate, helpful responses
3. ALWAYS cite your sources - mention who said what and when
4. If giving recommendations, explain your reasoning

PROJECT CONTEXT (Information from this project):
{context_with_sources}

---

USER MESSAGE from {user_name}:
{message}

---

RESPONSE GUIDELINES:

1. **If user is ASKING a question:**
   - Answer using the context above
   - CITE the source: "As per [person] on [date]..." or "According to [source]..."
   - If info not in context, say so clearly and give general guidance

2. **If user is SHARING information:**
   - Acknowledge: "Noted. [summary of what you understood]"
   - Confirm it's saved: "This has been recorded for project reference."
   - If this CHANGES something previously recorded, flag it clearly

3. **If user is REPORTING an issue:**
   - Acknowledge the issue seriously
   - Check if related issues exist in context
   - Give practical recommendations with reasoning
   - Flag if it needs escalation

4. **If user is making a DECISION:**
   - Confirm what was decided
   - Note if this changes anything from before
   - Remind about any approvals needed

CITATION FORMAT:
- "Column size is 450mm (confirmed by Rajesh on Dec 2)"
- "As discussed with architect on Nov 15, use M30 concrete"
- "Based on the drawing shared on Dec 5..."

LANGUAGE:
- Respond in the same language as the user (Hindi/Hinglish if they used it)
- Be direct and practical - site engineers need quick, clear info
- Use construction terminology they understand

Remember: You have access to ALL project discussions. Use them. Cite them."""

        try:
            result = await gemini_service._generate(prompt)
            
            return {
                "answer": result,
                "context_used": len(context),
                "sources": [c.get("source", "") for c in context if c.get("source")],
            }
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return {
                "answer": f"Sorry, I couldn't process that right now. Please try again.\n\nYour message has been saved: \"{message[:50]}...\"",
                "error": str(e),
            }
    
    async def _process_with_photo(
        self,
        message: str,
        photo_data: bytes,
        context: List[Dict],
        user_name: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Analyze photo with AI and project context
        """
        
        context_with_sources = self._format_context_for_citations(context)
        
        prompt = f"""Analyze this construction site photo.

USER'S MESSAGE: {message}
SENT BY: {user_name}

PROJECT CONTEXT (Specifications and past discussions):
{context_with_sources}

---

YOUR ANALYSIS SHOULD:

1. **Describe what you see** - Be specific about construction elements

2. **Check against specifications** - Compare with project context above
   - Does this match what was specified?
   - Any deviations from approved specs?
   - Cite the relevant specification when comparing

3. **Flag any concerns** with ⚠️
   - Quality issues
   - Safety concerns  
   - Deviations from specs
   - Things that need attention

4. **Give practical recommendations**
   - What action to take
   - Who to inform
   - What to check

CITATION FORMAT:
- "This appears to be 10mm rebar, but specification (shared Dec 5) requires 12mm"
- "Spacing looks like 200mm c/c, matches the approved drawing"

Respond in the user's language (Hindi/Hinglish if that's what they used)."""

        try:
            result = await gemini_service.analyze_image(
                image_data=photo_data,
                prompt=prompt,
            )
            
            return {
                "answer": result.get("analysis", "Could not analyze the photo."),
                "context_used": len(context),
                "photo_analyzed": True,
            }
            
        except Exception as e:
            logger.error(f"Photo analysis error: {e}")
            return {
                "answer": "Sorry, I couldn't analyze this photo. Please try again.\n\nThe photo has been saved to project records.",
                "error": str(e),
            }
    
    # =========================================================================
    # CONTEXT FORMATTING - For proper citations
    # =========================================================================
    
    def _format_context_for_citations(self, context: List[Dict]) -> str:
        """
        Format context so AI can cite sources properly
        
        Each piece of context includes:
        - The content
        - Who shared it
        - When
        - What type (decision, issue, conversation, etc.)
        """
        
        if not context:
            return "(No previous project discussions found. This might be a new project or new topic.)"
        
        formatted = []
        for i, item in enumerate(context, 1):
            # Use raw_content if available (has full context), fallback to content
            raw = item.get("raw_content", "")
            content = item.get("content", str(item))
            title = item.get("title", "")
            created_at = item.get("created_at", "")
            metadata = item.get("metadata", {})
            
            # Use raw content if content is empty (extraction issue)
            if not content and raw:
                content = raw
            
            # Extract source info from raw content format: [TYPE] [Project: X] [Date: Y] User: Content
            import re
            
            # Try to extract user from content
            user_match = re.search(r'(?:^|\]\s+)([A-Za-z\s]+):\s', content)
            user = user_match.group(1).strip() if user_match else metadata.get("user_name", "Unknown")
            
            # Extract date from raw content or created_at
            date_str = ""
            date_match = re.search(r'\[Date:\s*([^\]]+)\]', raw or content)
            if date_match:
                date_str = date_match.group(1)
            elif created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %d, %Y")
                except:
                    date_str = created_at[:10] if len(str(created_at)) > 10 else str(created_at)
            
            # Extract type from raw
            type_match = re.search(r'^\[([A-Z]+)\]', raw or "")
            mem_type = type_match.group(1) if type_match else "INFO"
            
            # Clean up content for display (remove metadata tags)
            display_content = re.sub(r'\[[^\]]+\]\s*', '', content).strip()
            if not display_content:
                display_content = content
            
            # Build citation-ready format
            source_line = f"📌 Source: {user} on {date_str}" if date_str else f"📌 Source: {user}"
            
            # Use title if available and content is short
            if title and len(display_content) < 20:
                display_content = f"{title}: {display_content}"
            
            formatted.append(f"{i}. {display_content}\n   {source_line}")
        
        return "\n\n".join(formatted)
    
    # =========================================================================
    # MEMORY OPERATIONS - Store everything
    # =========================================================================
    
    async def _store_incoming(
        self,
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str,
        message: str,
        has_photo: bool,
    ) -> str:
        """
        Store incoming message immediately (info dump)
        
        Everything shared becomes searchable:
        - "Column C1 is 450mm" → Searchable spec
        - "Architect said use M30" → Searchable decision
        - "Crack in beam B2" → Searchable issue
        """
        
        metadata = {
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat(),
            "has_photo": has_photo,
            "type": "incoming",
        }
        
        try:
            memory = await memory_service.add_memory(
                company_id=company_id,
                project_id=project_id,
                content=f"{user_name}: {message}" if user_name else message,
                memory_type="info",
                metadata=metadata,
                user_id=user_id,
            )
            logger.info(f"💾 Stored incoming message")
            return memory.id if hasattr(memory, 'id') else ""
        except Exception as e:
            logger.error(f"Failed to store incoming: {e}")
            return ""
    
    async def _store_response(
        self,
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str,
        question: str,
        answer: str,
    ) -> None:
        """
        Store the Q&A for future reference
        """
        
        content = f"Q ({user_name}): {question}\n\nA (SiteMind): {answer}"
        
        metadata = {
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "conversation",
        }
        
        try:
            await memory_service.add_memory(
                company_id=company_id,
                project_id=project_id,
                content=content,
                memory_type="conversation",
                metadata=metadata,
                user_id=user_id,
            )
            logger.info(f"💾 Stored conversation")
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
    
    async def _get_context(
        self,
        company_id: str,
        project_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get all relevant context from Supermemory
        """
        
        try:
            results = await memory_service.search(
                company_id=company_id,
                query=query,
                project_id=project_id,
                limit=limit,
            )
            return results
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return []
    
    # =========================================================================
    # SEARCH - For dashboard and direct queries
    # =========================================================================
    
    async def search(
        self,
        company_id: str,
        project_id: str,
        query: str,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Search project history
        
        Use for:
        - Dashboard search
        - "Find all discussions about columns"
        - "What decisions were made last week"
        """
        
        return await self._get_context(
            company_id=company_id,
            project_id=project_id,
            query=query,
            limit=limit,
        )
    
    async def get_recent_activity(
        self,
        company_id: str,
        project_id: str,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Get recent project activity for dashboard
        """
        
        return await self._get_context(
            company_id=company_id,
            project_id=project_id,
            query="recent activity conversation decision issue",
            limit=limit,
        )


# Singleton
sitemind_core = SiteMindCore()
