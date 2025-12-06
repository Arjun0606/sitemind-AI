"""
SiteMind WhatsApp Client
Twilio WhatsApp Business API integration
"""

import time
import asyncio
from typing import Optional, Dict, Any, List
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException

from config import settings
from utils.logger import logger
from utils.helpers import format_phone_number, extract_phone_number


class WhatsAppClient:
    """
    WhatsApp Business API Client using Twilio
    Handles sending and receiving WhatsApp messages
    """
    
    # Maximum message length for WhatsApp
    MAX_MESSAGE_LENGTH = 4096
    
    def __init__(self):
        """Initialize WhatsApp client"""
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            logger.warning("Twilio credentials not configured")
            self.is_configured = False
            return
        
        self.client = TwilioClient(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_whatsapp_number
        self.is_configured = True
        
        logger.info("WhatsApp client initialized successfully")
    
    async def send_message(
        self,
        to: str,
        body: str,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message
        
        Args:
            to: Recipient phone number (with or without whatsapp: prefix)
            body: Message text
            media_url: Optional URL to media file (image, PDF)
        
        Returns:
            Dict with message_sid, status, response_time_ms
        """
        if not self.is_configured:
            return {
                "message_sid": None,
                "status": "failed",
                "error": "WhatsApp client not configured",
                "response_time_ms": 0,
            }
        
        start_time = time.time()
        
        try:
            # Format the recipient number
            to_formatted = format_phone_number(to)
            
            # Truncate message if too long
            if len(body) > self.MAX_MESSAGE_LENGTH:
                body = body[:self.MAX_MESSAGE_LENGTH - 50] + "\n\n... (message truncated)"
            
            # Build message parameters
            message_params = {
                "from_": self.from_number,
                "to": to_formatted,
                "body": body,
            }
            
            # Add media if provided
            if media_url:
                message_params["media_url"] = [media_url]
            
            # Send message (run in thread to avoid blocking)
            message = await asyncio.to_thread(
                self._send_message_sync,
                message_params
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"WhatsApp message sent to {to_formatted}: {message.sid} ({elapsed_ms}ms)")
            
            return {
                "message_sid": message.sid,
                "status": message.status,
                "response_time_ms": elapsed_ms,
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending message: {e}")
            return {
                "message_sid": None,
                "status": "failed",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return {
                "message_sid": None,
                "status": "failed",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000),
            }
    
    def _send_message_sync(self, params: dict):
        """Synchronous message send (called via asyncio.to_thread)"""
        return self.client.messages.create(**params)
    
    async def send_template_message(
        self,
        to: str,
        template_sid: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp template message (for initiating conversations)
        
        Args:
            to: Recipient phone number
            template_sid: Twilio content template SID
            variables: Template variables
        
        Returns:
            Dict with message_sid and status
        """
        if not self.is_configured:
            return {
                "message_sid": None,
                "status": "failed",
                "error": "WhatsApp client not configured",
            }
        
        start_time = time.time()
        
        try:
            to_formatted = format_phone_number(to)
            
            message_params = {
                "from_": self.from_number,
                "to": to_formatted,
                "content_sid": template_sid,
            }
            
            if variables:
                message_params["content_variables"] = str(variables)
            
            message = await asyncio.to_thread(
                self._send_message_sync,
                message_params
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            return {
                "message_sid": message.sid,
                "status": message.status,
                "response_time_ms": elapsed_ms,
            }
            
        except Exception as e:
            logger.error(f"Failed to send template message: {e}")
            return {
                "message_sid": None,
                "status": "failed",
                "error": str(e),
            }
    
    async def send_welcome_message(self, to: str, project_name: str) -> Dict[str, Any]:
        """
        Send welcome message to a new site engineer
        
        Args:
            to: Engineer's phone number
            project_name: Name of the project they're added to
        
        Returns:
            Message result
        """
        welcome_text = f"""🏗️ *Welcome to SiteMind!*

You've been added as a team member for *{project_name}*.

I'm your AI Site Engineer assistant. I can help you with:

📐 *Blueprint Questions*
"What's the beam size at grid B2?"
"Show me column spacing on floor 3"

🎤 *Voice Notes*
Send me a voice message and I'll understand your query

📷 *Site Photos*
Send a photo and ask "Is this placement correct?"

💡 *Tips:*
• Be specific with grid references
• I'll always cite the drawing number
• If unsure, I'll tell you to verify with the architect

Let's build something great together! 🚀"""
        
        return await self.send_message(to=to, body=welcome_text)
    
    async def download_media(self, media_url: str) -> Optional[bytes]:
        """
        Download media from Twilio CDN
        
        Args:
            media_url: URL from incoming WhatsApp message
        
        Returns:
            Media content as bytes, or None if failed
        """
        try:
            import httpx
            
            # Twilio media URLs require authentication
            async with httpx.AsyncClient(
                auth=(settings.twilio_account_sid, settings.twilio_auth_token)
            ) as client:
                response = await client.get(media_url, timeout=60.0)
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            return None
    
    def validate_webhook_signature(
        self,
        signature: str,
        url: str,
        params: dict,
    ) -> bool:
        """
        Validate Twilio webhook signature for security
        
        Args:
            signature: X-Twilio-Signature header
            url: Full webhook URL
            params: POST parameters
        
        Returns:
            True if valid, False otherwise
        """
        from twilio.request_validator import RequestValidator
        
        validator = RequestValidator(settings.twilio_auth_token)
        return validator.validate(url, params, signature)
    
    def get_message_status(self, message_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a sent message
        
        Args:
            message_sid: Twilio message SID
        
        Returns:
            Dict with status info or None
        """
        if not self.is_configured:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                "sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
            }
        except Exception as e:
            logger.error(f"Failed to get message status: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if WhatsApp service is healthy"""
        if not self.is_configured:
            return {"status": "not_configured", "error": "Twilio credentials not set"}
        
        try:
            # Fetch account info to verify credentials
            account = await asyncio.to_thread(
                lambda: self.client.api.accounts(settings.twilio_account_sid).fetch()
            )
            return {
                "status": "healthy",
                "account_status": account.status,
                "from_number": self.from_number,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
whatsapp_client = WhatsAppClient()

