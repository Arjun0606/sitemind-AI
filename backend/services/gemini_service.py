"""
SiteMind Gemini Service
AI-powered analysis using Google Gemini

CAPABILITIES:
- Text queries (construction questions)
- Image analysis (site photos, blueprints)
- Document analysis (PDFs)
- Multi-turn conversations
"""

from typing import Dict, Any, List, Optional
import httpx
import json
import base64

from config import settings
from utils.logger import logger


class GeminiService:
    """
    Google Gemini API wrapper for construction AI
    
    Using Gemini 3 Pro - Google's most intelligent model
    https://ai.google.dev/gemini-api/docs
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Fallback models in order of preference
        self.fallback_models = [
            "gemini-3-pro",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
        ]
        
        # System prompt for construction context
        self.system_prompt = """You are SiteMind, a senior construction expert with 20+ years of experience in Indian construction.

YOUR EXPERTISE:
- RCC structures (IS 456, IS 13920)
- Steel structures (IS 800)
- Foundation engineering (IS 1904, IS 2911)
- Concrete technology (IS 10262)
- Quality control and testing
- Construction safety (BOCW Act)
- Project management
- Cost estimation

YOUR PERSONALITY:
- Practical, not just theoretical
- Safety-first mindset
- Direct and clear communication
- References codes but explains in simple terms
- Shares real-world tips and warnings

LANGUAGE RULES (CRITICAL):
- DETECT the language of the user's message
- RESPOND in the SAME language they used
- If they write in Hindi, respond in Hindi
- If they write in Hinglish (mix of Hindi+English), respond in Hinglish
- If they write in English, respond in English
- Use simple, construction-site friendly language
- Example Hindi: "Column ka cover IS 456 ke hisaab se 40mm hona chahiye"
- Example Hinglish: "Minimum cover 40mm hai as per IS 456"

CONVERSATION CONTINUITY (CRITICAL):
- Look at the CONVERSATION HISTORY in the context
- If user says "and for beams?" after asking about columns, UNDERSTAND the context
- If user says "what about that?" - refer to previous topic
- Maintain context across messages like a real conversation
- Don't ask "what do you mean?" if context is clear from history

RESPONSE FORMAT:
1. Answer the question directly first
2. Reference relevant IS code if applicable
3. Add practical tip from field experience
4. Flag any safety concerns
5. Mention if something needs architect/engineer approval

IMPORTANT RULES:
- Never compromise on safety
- If unsure, say "Please verify with structural engineer" (or Hindi equivalent)
- Always mention when changes need formal approval
- Use Indian construction terminology
- Understand that site engineers may not have engineering background
- Keep responses concise for WhatsApp (under 1000 characters ideally)

EXAMPLE RESPONSE STYLE (English):
"The minimum cover for columns as per IS 456 is 40mm.

In coastal areas, use 50mm minimum.

💡 Tip: Check cover blocks before pouring - #1 cause of corrosion.

⚠️ If less than 40mm, stop work and fix it."

EXAMPLE RESPONSE STYLE (Hindi):
"IS 456 ke according column ka minimum cover 40mm hona chahiye.

Coastal areas mein 50mm use karein.

💡 Tip: Concrete dalne se pehle cover blocks check karein - yeh sabse common problem hai.

⚠️ Agar 40mm se kam hai, toh kaam rok do aur pehle fix karo."
"""
    
    def _is_configured(self) -> bool:
        """Check if Gemini is configured"""
        return (
            self.api_key and
            self.api_key != "your_google_api_key" and
            len(self.api_key) > 10
        )
    
    # =========================================================================
    # TEXT QUERIES
    # =========================================================================
    
    async def query(
        self,
        question: str,
        context: List[Dict] = None,
        project_info: Dict = None,
    ) -> Dict[str, Any]:
        """
        Answer a construction query
        
        Args:
            question: The query from site engineer
            context: Relevant context from memory
            project_info: Project details
            
        Returns:
            Response with answer and metadata
        """
        if not self._is_configured():
            logger.warning("Gemini not configured, returning fallback")
            return {
                "answer": "⚠️ AI not configured. Please set up GOOGLE_API_KEY.",
                "status": "unconfigured",
            }
        
        # Build prompt
        prompt_parts = []
        
        # Add project context
        if project_info:
            prompt_parts.append(f"**Project:** {project_info.get('name', 'Unknown')}")
            prompt_parts.append(f"**Type:** {project_info.get('project_type', 'Unknown')}")
            prompt_parts.append("")
        
        # Add conversation history FIRST (critical for continuity!)
        if context:
            # Separate conversation history from other context
            conversation = None
            other_context = []
            
            for item in context:
                if item.get("is_conversation") or item.get("type") == "conversation_history":
                    conversation = item.get("content", "")
                else:
                    other_context.append(item)
            
            # Add conversation history prominently
            if conversation:
                prompt_parts.append("**Recent Conversation (for context):**")
                prompt_parts.append(conversation)
                prompt_parts.append("")
            
            # Add other relevant context
            if other_context:
                prompt_parts.append("**Relevant Project Context:**")
                for item in other_context[:5]:  # Max 5 context items
                    content = item.get("content", str(item))
                    prompt_parts.append(f"- {content[:200]}...")
                prompt_parts.append("")
        
        # Add question
        prompt_parts.append(f"**Current Question:** {question}")
        prompt_parts.append("")
        prompt_parts.append("(Remember: Respond in the same language as the question. If it's a follow-up, use conversation context.)")
        
        full_prompt = "\n".join(prompt_parts)
        
        try:
            response = await self._generate(full_prompt)
            return {
                "answer": response,
                "status": "success",
                "model": self.model,
            }
        except Exception as e:
            logger.error(f"Gemini query error: {e}")
            return {
                "answer": f"❌ Error processing query: {str(e)}",
                "status": "error",
                "error": str(e),
            }
    
    async def _generate(
        self,
        prompt: str,
        image_data: bytes = None,
        mime_type: str = None,
    ) -> str:
        """Generate content from Gemini with automatic fallback"""
        
        # Build content parts
        parts = []
        
        # Add image if provided
        if image_data:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type or "image/jpeg",
                    "data": base64.b64encode(image_data).decode("utf-8"),
                }
            })
        
        # Add text
        parts.append({"text": prompt})
        
        payload = {
            "system_instruction": {
                "parts": [{"text": self.system_prompt}]
            },
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            },
        }
        
        # Try models in order of preference
        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]
        last_error = None
        
        async with httpx.AsyncClient() as client:
            for model in models_to_try:
                url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
                
                try:
                    response = await client.post(url, json=payload, timeout=60.0)
                    
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            content = candidates[0].get("content", {})
                            resp_parts = content.get("parts", [])
                            if resp_parts:
                                # Update active model on success
                                if model != self.model:
                                    logger.info(f"🔄 Using fallback model: {model}")
                                    self.model = model
                                return resp_parts[0].get("text", "")
                        return "No response generated"
                    elif response.status_code == 404:
                        # Model not found, try next
                        logger.warning(f"Model {model} not available, trying next...")
                        continue
                    else:
                        error = response.json().get("error", {})
                        last_error = error.get("message", f"API error: {response.status_code}")
                        # Try next model
                        continue
                        
                except Exception as e:
                    last_error = str(e)
                    continue
        
        raise Exception(last_error or "All models failed")
    
    # =========================================================================
    # IMAGE ANALYSIS
    # =========================================================================
    
    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        caption: str = None,
        analysis_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Analyze a construction site image
        
        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type
            caption: Optional user caption
            analysis_type: Type of analysis (progress, issue, verification)
        """
        if not self._is_configured():
            return {"analysis": "AI not configured", "status": "unconfigured"}
        
        prompts = {
            "general": "Analyze this construction site image. Identify any issues, materials, work quality, and safety concerns.",
            "progress": "Analyze this progress photo. Describe what stage of construction is shown and any observations about quality.",
            "issue": "This image shows a potential issue. Identify the problem, assess its severity, and recommend solutions.",
            "verification": "Verify the work shown in this image against standard construction practices. Note any concerns.",
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        if caption:
            prompt += f"\n\nUser note: {caption}"
        
        try:
            response = await self._generate(prompt, image_data, mime_type)
            return {
                "analysis": response,
                "status": "success",
                "analysis_type": analysis_type,
            }
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                "analysis": f"Error analyzing image: {str(e)}",
                "status": "error",
            }
    
    # =========================================================================
    # DOCUMENT ANALYSIS
    # =========================================================================
    
    async def analyze_document(
        self,
        document_text: str,
        document_type: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Analyze document content
        
        Args:
            document_text: Extracted text from document
            document_type: Type of document (specification, change_order, etc.)
        """
        if not self._is_configured():
            return {"analysis": "AI not configured", "status": "unconfigured"}
        
        prompt = f"""Analyze this construction document:

**Document Type:** {document_type}

**Content:**
{document_text[:5000]}

Please:
1. Summarize the key points
2. Extract any specifications or quantities
3. Identify any changes from previous versions (if apparent)
4. Flag any concerns or ambiguities
"""
        
        try:
            response = await self._generate(prompt)
            return {
                "analysis": response,
                "status": "success",
                "document_type": document_type,
            }
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            return {
                "analysis": f"Error analyzing document: {str(e)}",
                "status": "error",
            }
    
    # =========================================================================
    # SPECIALIZED QUERIES
    # =========================================================================
    
    async def check_specification(
        self,
        item: str,
        specification: str,
        code_reference: str = None,
    ) -> Dict[str, Any]:
        """Check if a specification is correct"""
        prompt = f"""Verify this construction specification:

**Item:** {item}
**Specification:** {specification}
"""
        if code_reference:
            prompt += f"**Code Reference:** {code_reference}"
        
        prompt += """

Please:
1. Verify if the specification is correct
2. Reference relevant IS codes or standards
3. Flag any concerns
4. Provide the recommended specification if different
"""
        
        try:
            response = await self._generate(prompt)
            return {"answer": response, "status": "success"}
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "status": "error"}
    
    async def detect_conflicts(
        self,
        changes: List[str],
        context: str = None,
    ) -> Dict[str, Any]:
        """Detect conflicts between changes"""
        prompt = f"""Analyze these proposed changes for conflicts:

**Changes:**
"""
        for i, change in enumerate(changes, 1):
            prompt += f"{i}. {change}\n"
        
        if context:
            prompt += f"\n**Context:**\n{context}"
        
        prompt += """

Please:
1. Identify any conflicts between changes
2. Flag any safety concerns
3. Suggest resolution if conflicts exist
"""
        
        try:
            response = await self._generate(prompt)
            return {"analysis": response, "status": "success"}
        except Exception as e:
            return {"analysis": f"Error: {str(e)}", "status": "error"}


# Singleton instance
gemini_service = GeminiService()
