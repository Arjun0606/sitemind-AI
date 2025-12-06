"""
SiteMind Whisper Service
OpenAI Whisper integration for voice note transcription
"""

import time
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from openai import OpenAI, AsyncOpenAI

from config import settings
from utils.logger import logger


class WhisperService:
    """
    OpenAI Whisper Service
    Handles voice note transcription for WhatsApp voice messages
    """
    
    # Supported audio formats
    SUPPORTED_FORMATS = {
        "audio/ogg",           # WhatsApp default
        "audio/mpeg",          # MP3
        "audio/mp4",           # M4A
        "audio/wav",           # WAV
        "audio/webm",          # WebM
        "audio/x-m4a",         # M4A variant
        "audio/ogg; codecs=opus",  # OGG Opus (WhatsApp)
    }
    
    def __init__(self):
        """Initialize Whisper service"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.is_configured = False
            return
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.async_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.is_configured = True
        
        logger.info("Whisper service initialized successfully")
    
    async def transcribe_audio(
        self,
        audio_url: str,
        content_type: str = "audio/ogg",
    ) -> Dict[str, Any]:
        """
        Transcribe audio from URL (typically WhatsApp CDN)
        
        Args:
            audio_url: URL to the audio file
            content_type: MIME type of the audio
        
        Returns:
            Dict with transcription, duration, response_time_ms
        """
        if not self.is_configured:
            return {
                "transcription": "",
                "duration_seconds": 0,
                "response_time_ms": 0,
                "error": "Whisper service not configured"
            }
        
        start_time = time.time()
        
        try:
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url, timeout=30.0)
                response.raise_for_status()
                audio_data = response.content
            
            download_time = time.time() - start_time
            logger.debug(f"Audio downloaded in {download_time:.2f}s ({len(audio_data)} bytes)")
            
            # Save to temporary file (Whisper needs a file)
            suffix = self._get_file_extension(content_type)
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe using Whisper
                with open(tmp_path, "rb") as audio_file:
                    transcript = await asyncio.to_thread(
                        self._transcribe_sync,
                        audio_file
                    )
                
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                # Estimate duration (rough: 16KB per second for OGG)
                duration_estimate = len(audio_data) / 16000
                
                logger.info(f"Audio transcribed in {elapsed_ms}ms: {transcript[:100]}...")
                
                return {
                    "transcription": transcript,
                    "duration_seconds": duration_estimate,
                    "response_time_ms": elapsed_ms,
                }
                
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to download audio: {e}")
            return {
                "transcription": "",
                "duration_seconds": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "error": f"Failed to download audio: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return {
                "transcription": "",
                "duration_seconds": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "error": str(e)
            }
    
    def _transcribe_sync(self, audio_file) -> str:
        """Synchronous transcription (called via asyncio.to_thread)"""
        transcript = self.client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            language="en",  # English only as per requirements
            response_format="text",
        )
        return transcript.strip()
    
    async def transcribe_bytes(
        self,
        audio_data: bytes,
        content_type: str = "audio/ogg",
    ) -> Dict[str, Any]:
        """
        Transcribe audio from bytes
        
        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of the audio
        
        Returns:
            Dict with transcription, duration, response_time_ms
        """
        if not self.is_configured:
            return {
                "transcription": "",
                "duration_seconds": 0,
                "response_time_ms": 0,
                "error": "Whisper service not configured"
            }
        
        start_time = time.time()
        
        try:
            suffix = self._get_file_extension(content_type)
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                with open(tmp_path, "rb") as audio_file:
                    transcript = await asyncio.to_thread(
                        self._transcribe_sync,
                        audio_file
                    )
                
                elapsed_ms = int((time.time() - start_time) * 1000)
                duration_estimate = len(audio_data) / 16000
                
                return {
                    "transcription": transcript,
                    "duration_seconds": duration_estimate,
                    "response_time_ms": elapsed_ms,
                }
                
            finally:
                Path(tmp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return {
                "transcription": "",
                "duration_seconds": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "error": str(e)
            }
    
    def _get_file_extension(self, content_type: str) -> str:
        """Get file extension from content type"""
        mapping = {
            "audio/ogg": ".ogg",
            "audio/ogg; codecs=opus": ".ogg",
            "audio/mpeg": ".mp3",
            "audio/mp4": ".m4a",
            "audio/x-m4a": ".m4a",
            "audio/wav": ".wav",
            "audio/webm": ".webm",
        }
        return mapping.get(content_type, ".ogg")
    
    def is_supported_format(self, content_type: str) -> bool:
        """Check if audio format is supported"""
        return content_type in self.SUPPORTED_FORMATS
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Whisper service is healthy"""
        if not self.is_configured:
            return {"status": "not_configured", "error": "API key not set"}
        
        try:
            # We can't easily test Whisper without audio, so just check the client
            # A more robust check would involve a test audio file
            return {"status": "healthy", "model": settings.whisper_model}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
whisper_service = WhisperService()

