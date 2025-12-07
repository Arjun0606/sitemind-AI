"""
SiteMind Gemini Service
AI-powered construction intelligence using Google Gemini

FEATURES:
- Blueprint analysis (text extraction, dimensions, specs)
- Image understanding (site photos, drawings)
- Query answering with context
- Multi-turn conversations
- Construction-specific prompting
"""

from typing import Optional, List, Dict, Any
import base64
import httpx
import json

from config import settings
from utils.logger import logger


class GeminiService:
    """
    Google Gemini API wrapper for construction AI
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.model = settings.GEMINI_MODEL  # gemini-2.0-flash or gemini-2.5-pro
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # System prompt for construction context
        self.system_prompt = """You are SiteMind, an expert AI construction assistant. You help site engineers, project managers, and builders with:

1. BLUEPRINT QUERIES: Answer questions about structural specifications, dimensions, rebar details, material grades
2. CONSTRUCTION KNOWLEDGE: Provide accurate information about construction methods, IS codes, best practices
3. PROJECT CONTEXT: Use provided context from project memory to give specific answers
4. SAFETY: Always emphasize safety-critical information

RESPONSE GUIDELINES:
- Be concise but complete
- Include specific numbers and references
- Cite drawings/documents when available (e.g., "Per drawing SK-003...")
- Use both English and Hindi terms when helpful (e.g., "column (khamba)")
- If unsure, say so rather than guessing
- For safety-related queries, always add appropriate warnings

FORMATTING:
- Use **bold** for important values
- Use bullet points for lists
- Keep responses under 500 words unless detailed explanation needed"""
    
    async def query(
        self,
        query: str,
        context: List[Dict] = None,
        project_id: str = None,
        images: List[str] = None,
    ) -> str:
        """
        Answer a construction query using Gemini
        
        Args:
            query: The user's question
            context: Retrieved context from memory
            project_id: Project identifier for logging
            images: Optional list of base64 encoded images
            
        Returns:
            AI-generated response
        """
        # Build prompt with context
        prompt = self._build_prompt(query, context)
        
        # Call Gemini API
        response = await self._call_gemini(prompt, images)
        
        logger.info(f"🤖 Gemini query processed: {query[:50]}...")
        
        return response
    
    async def analyze_document(
        self,
        document_base64: str,
        document_type: str = "pdf",
        extraction_focus: str = None,
    ) -> Dict[str, Any]:
        """
        Analyze a construction document (drawing, specification)
        
        Args:
            document_base64: Base64 encoded document
            document_type: pdf, image, etc.
            extraction_focus: Specific area to focus on
            
        Returns:
            Extracted information
        """
        prompt = f"""Analyze this construction document and extract:

1. DOCUMENT TYPE: (structural drawing, architectural plan, specification, etc.)
2. DRAWING NUMBER: If visible
3. REVISION: If visible
4. KEY SPECIFICATIONS:
   - Dimensions (beams, columns, slabs)
   - Rebar details (bar sizes, spacing)
   - Material grades
   - Grid references
5. NOTES: Any important notes or instructions

{f"Focus especially on: {extraction_focus}" if extraction_focus else ""}

Return structured information that can be searched later."""

        response = await self._call_gemini(prompt, [document_base64])
        
        return {
            "analysis": response,
            "document_type": document_type,
            "timestamp": "now",
        }
    
    async def analyze_site_photo(
        self,
        photo_base64: str,
        caption: str = None,
        expected_work: str = None,
    ) -> Dict[str, Any]:
        """
        Analyze a site photo for progress/quality
        
        Args:
            photo_base64: Base64 encoded image
            caption: User's caption
            expected_work: What work should be visible
            
        Returns:
            Analysis results
        """
        prompt = f"""Analyze this construction site photo:

{f"Caption from engineer: {caption}" if caption else ""}
{f"Expected work: {expected_work}" if expected_work else ""}

Identify:
1. WORK VISIBLE: What construction activity is shown
2. STAGE: What construction stage does this appear to be
3. ESTIMATED PROGRESS: Rough percentage if determinable
4. QUALITY OBSERVATIONS: Any visible issues or concerns
5. SAFETY: Any safety concerns visible

Be specific and practical in your assessment."""

        response = await self._call_gemini(prompt, [photo_base64])
        
        return {
            "analysis": response,
            "caption": caption,
        }
    
    async def detect_conflicts(
        self,
        items: List[Dict],
    ) -> List[Dict]:
        """
        Detect conflicts between multiple specifications
        
        Args:
            items: List of specifications/decisions to compare
            
        Returns:
            List of detected conflicts
        """
        if len(items) < 2:
            return []
        
        prompt = f"""Compare these construction specifications and identify any conflicts:

{json.dumps(items, indent=2)}

For each conflict found, provide:
1. CONFLICT: What values/specs conflict
2. ITEMS: Which items conflict
3. SEVERITY: High/Medium/Low
4. RECOMMENDATION: How to resolve

If no conflicts, return "No conflicts detected"."""

        response = await self._call_gemini(prompt)
        
        # Parse response for conflicts
        # In production, use structured output
        return [{"raw_analysis": response}]
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _build_prompt(self, query: str, context: List[Dict] = None) -> str:
        """Build the full prompt with context"""
        prompt_parts = [self.system_prompt]
        
        # Add context if available
        if context:
            prompt_parts.append("\n--- PROJECT CONTEXT ---")
            for i, ctx in enumerate(context[:5], 1):  # Limit context
                content = ctx.get("content", ctx.get("text", str(ctx)))
                source = ctx.get("source", "project memory")
                prompt_parts.append(f"\n[{i}] Source: {source}\n{content}")
            prompt_parts.append("\n--- END CONTEXT ---\n")
        
        # Add the query
        prompt_parts.append(f"\nUser Query: {query}")
        prompt_parts.append("\nProvide a helpful, accurate response:")
        
        return "\n".join(prompt_parts)
    
    async def _call_gemini(
        self,
        prompt: str,
        images: List[str] = None,
    ) -> str:
        """Call the Gemini API"""
        
        # Check if API key is configured
        if not self.api_key or self.api_key == "your_google_api_key":
            logger.warning("Gemini API key not configured, using mock response")
            return self._mock_response(prompt)
        
        # Build request
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        # Build content parts
        parts = [{"text": prompt}]
        
        # Add images if provided
        if images:
            for img in images:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img,
                    }
                })
        
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract text from response
                    candidates = result.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if parts:
                            return parts[0].get("text", "No response generated")
                    
                    return "No response generated"
                else:
                    error = response.json()
                    logger.error(f"Gemini API error: {error}")
                    return f"I encountered an error processing your request. Please try again."
                    
        except Exception as e:
            logger.error(f"Gemini API exception: {e}")
            return "I'm having trouble connecting right now. Please try again in a moment."
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for development"""
        # Extract query from prompt
        if "beam" in prompt.lower():
            return """Based on the project specifications:

**Beam B3 at Floor 2**
- Size: 300 × 600 mm
- Main reinforcement: 
  - Top: 4 nos. 20mm dia
  - Bottom: 4 nos. 20mm dia
- Stirrups: 8mm @ 150mm c/c

*Reference: Drawing SK-003, Grid B-3*

Note: Always verify on-site dimensions before formwork."""

        elif "column" in prompt.lower() or "khamba" in prompt.lower():
            return """**Column C4 Specifications:**

- Size: 450 × 450 mm
- Reinforcement: 8 nos. 20mm dia
- Ties: 8mm @ 150mm c/c
- Concrete Grade: M30

*Reference: Drawing SK-001*

The column extends from foundation to terrace level with lap at floor levels."""

        elif "slab" in prompt.lower():
            return """**Slab Details:**

- Thickness: 150mm
- Main reinforcement: 10mm @ 150mm c/c (both ways)
- Distribution: 8mm @ 200mm c/c
- Cover: 25mm

*Reference: Drawing SK-005*"""

        else:
            return """I can help you with project specifications. Try asking about:

• Beam dimensions and reinforcement
• Column specifications
• Slab details
• Rebar requirements
• Material grades

Please provide specific element references (e.g., "B3", "C4") for accurate information."""


# Singleton instance
gemini_service = GeminiService()
