"""
SiteMind Gemini Service
Google Gemini AI integration for blueprint analysis and query answering
"""

import time
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from config import settings
from utils.logger import logger


class GeminiService:
    """
    Google Gemini AI Service
    Handles blueprint analysis, query answering, and multimodal processing
    """
    
    # System instruction for SiteMind AI
    SYSTEM_INSTRUCTION = """You are 'SiteMind', an expert AI Site Engineer assistant for construction projects in India.

YOUR ROLE:
- You help site engineers get instant, accurate answers about construction blueprints and project details
- You prevent costly rework by providing precise information from blueprints
- You are the "AI colleague" that remembers everything about the project

CONTEXT YOU RECEIVE:
1. Project blueprints (PDFs) - Architectural, Structural, MEP drawings
2. Project history from memory - Past RFIs, change orders, decisions
3. User's query - What the site engineer needs to know

RESPONSE GUIDELINES:
1. BE PRECISE: When mentioning dimensions, always cite the exact measurement (e.g., "300mm x 600mm")
2. CITE SOURCES: Always reference the drawing number (e.g., "See Drawing ST-04, Grid B2")
3. FLAG CONFLICTS: If you notice discrepancies between drawings or memory, explicitly flag them
4. BE PROFESSIONAL: Respond in professional English, suitable for construction industry
5. BE CONCISE: Site engineers are busy - give direct answers first, details after
6. SAFETY FIRST: If a query involves safety-critical information, add appropriate warnings

RESPONSE FORMAT:
- Start with the direct answer
- Follow with the source reference
- Add any relevant context or warnings
- Keep responses under 500 words unless complex explanation needed

EXAMPLE RESPONSE:
"Beam B2 on 3rd floor is 300mm x 600mm (depth increased from 450mm in Revision 3 due to HVAC duct routing conflict). 

📐 Reference: Drawing ST-03, Grid Line B2
⚠️ Note: Ensure formwork accounts for the increased depth before pouring."

LIMITATIONS:
- If information is not in the provided blueprints or context, say so clearly
- Never guess or hallucinate dimensions - accuracy is critical
- If unsure, recommend the engineer verify with the architect/structural engineer"""

    def __init__(self):
        """Initialize Gemini service"""
        if not settings.google_api_key:
            logger.warning("Google API key not configured")
            self.is_configured = False
            return
            
        genai.configure(api_key=settings.google_api_key)
        self.is_configured = True
        
        # Safety settings - allow construction-related content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        # Generation config for accurate, deterministic responses
        self.generation_config = genai.GenerationConfig(
            temperature=0.1,  # Low temperature for accuracy
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )
        
        # Initialize models
        self.flash_model = GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=self.SYSTEM_INSTRUCTION,
            safety_settings=self.safety_settings,
            generation_config=self.generation_config,
        )
        
        self.pro_model = GenerativeModel(
            model_name=settings.gemini_pro_model,
            system_instruction=self.SYSTEM_INSTRUCTION,
            safety_settings=self.safety_settings,
            generation_config=self.generation_config,
        )
        
        # Cache for uploaded files
        self._file_cache: Dict[str, Any] = {}
        
        logger.info("Gemini service initialized successfully")
    
    async def upload_blueprint(
        self, 
        file_path: str,
        display_name: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Upload a blueprint PDF to Gemini for analysis
        
        Args:
            file_path: Local path or URL to the PDF file
            display_name: Optional display name for the file
        
        Returns:
            Dict with file_id and uri, or None if failed
        """
        if not self.is_configured:
            logger.error("Gemini service not configured")
            return None
            
        try:
            start_time = time.time()
            
            # Upload file to Gemini
            file = genai.upload_file(
                path=file_path,
                display_name=display_name or Path(file_path).name,
            )
            
            # Wait for processing to complete
            while file.state.name == "PROCESSING":
                await asyncio.sleep(1)
                file = genai.get_file(file.name)
            
            if file.state.name == "FAILED":
                logger.error(f"File processing failed: {file.name}")
                return None
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Blueprint uploaded successfully: {file.name} ({elapsed:.0f}ms)")
            
            # Cache the file reference
            self._file_cache[file.name] = file
            
            return {
                "file_id": file.name,
                "uri": file.uri,
                "display_name": file.display_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to upload blueprint: {e}")
            return None
    
    async def analyze_query(
        self,
        query: str,
        blueprint_ids: Optional[List[str]] = None,
        memory_context: Optional[str] = None,
        image_data: Optional[bytes] = None,
        use_pro_model: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze a query using blueprints and memory context
        
        Args:
            query: User's question
            blueprint_ids: List of Gemini file IDs to include
            memory_context: Retrieved context from Supermemory
            image_data: Optional image bytes (for site photo analysis)
            use_pro_model: Use Pro model for complex queries
        
        Returns:
            Dict with response, confidence, tokens_used, response_time_ms
        """
        if not self.is_configured:
            return {
                "response": "AI service not configured. Please contact support.",
                "confidence": 0,
                "tokens_used": 0,
                "response_time_ms": 0,
                "error": "Service not configured"
            }
        
        start_time = time.time()
        
        try:
            # Build the content parts
            content_parts = []
            
            # Add memory context if available
            if memory_context:
                content_parts.append(f"**PROJECT HISTORY & CONTEXT:**\n{memory_context}\n\n---\n\n")
            
            # Add blueprints
            if blueprint_ids:
                content_parts.append("**RELEVANT BLUEPRINTS:**\n")
                for file_id in blueprint_ids:
                    try:
                        file = genai.get_file(file_id)
                        content_parts.append(file)
                    except Exception as e:
                        logger.warning(f"Could not retrieve file {file_id}: {e}")
                content_parts.append("\n---\n\n")
            
            # Add image if provided
            if image_data:
                content_parts.append({
                    "mime_type": "image/jpeg",
                    "data": image_data
                })
                content_parts.append("\n**SITE PHOTO** (analyze this against the blueprints)\n\n")
            
            # Add the user query
            content_parts.append(f"**USER QUERY:**\n{query}")
            
            # Select model based on complexity
            model = self.pro_model if use_pro_model else self.flash_model
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                content_parts
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # Extract response text
            response_text = response.text if response.text else "I couldn't generate a response. Please try rephrasing your question."
            
            # Estimate tokens (rough approximation)
            tokens_used = len(query.split()) * 1.5 + len(response_text.split()) * 1.5
            
            logger.info(f"Query processed in {elapsed_ms}ms using {model.model_name}")
            
            return {
                "response": response_text,
                "confidence": 0.95,  # Could be enhanced with response analysis
                "tokens_used": int(tokens_used),
                "response_time_ms": elapsed_ms,
                "model_used": model.model_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze query: {e}")
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "response": "I encountered an error processing your query. Please try again.",
                "confidence": 0,
                "tokens_used": 0,
                "response_time_ms": elapsed_ms,
                "error": str(e)
            }
    
    async def analyze_site_photo(
        self,
        image_data: bytes,
        query: str,
        blueprint_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a site photo against blueprints
        
        Args:
            image_data: Image bytes
            query: User's question about the photo
            blueprint_ids: Related blueprint IDs
        
        Returns:
            Analysis result
        """
        return await self.analyze_query(
            query=query,
            blueprint_ids=blueprint_ids,
            image_data=image_data,
            use_pro_model=True,  # Use Pro for image analysis
        )
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an uploaded file"""
        try:
            file = genai.get_file(file_id)
            return {
                "file_id": file.name,
                "display_name": file.display_name,
                "uri": file.uri,
                "state": file.state.name,
                "size_bytes": getattr(file, 'size_bytes', None),
            }
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete an uploaded file from Gemini"""
        try:
            genai.delete_file(file_id)
            if file_id in self._file_cache:
                del self._file_cache[file_id]
            logger.info(f"File deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Gemini service is healthy"""
        if not self.is_configured:
            return {"status": "not_configured", "error": "API key not set"}
        
        try:
            # Simple test query
            response = await asyncio.to_thread(
                self.flash_model.generate_content,
                "Reply with 'OK' if you can read this."
            )
            
            if response.text and "OK" in response.text.upper():
                return {"status": "healthy", "model": settings.gemini_model}
            return {"status": "degraded", "error": "Unexpected response"}
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
gemini_service = GeminiService()

