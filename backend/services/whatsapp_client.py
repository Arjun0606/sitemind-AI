"""
SiteMind WhatsApp Client
Handles all outbound WhatsApp communication via Twilio

FEATURES:
- Send text messages
- Send media (images, documents)
- Message templates
- Rate limiting
- Error handling
"""

from typing import Optional, List, Dict, Any
import httpx
import base64
import asyncio
from datetime import datetime

from config import settings
from utils.logger import logger


class WhatsAppClient:
    """
    WhatsApp Business API client via Twilio
    """
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        # Rate limiting
        self._message_count = 0
        self._last_reset = datetime.utcnow()
        self._rate_limit = 100  # messages per minute
    
    async def send_message(
        self,
        to: str,
        body: str,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message
        
        Args:
            to: Recipient phone number (with country code)
            body: Message text
            media_url: Optional media URL to attach
            
        Returns:
            Twilio API response
        """
        # Format numbers
        to_formatted = self._format_number(to)
        from_formatted = self._format_number(self.from_number)
        
        # Check rate limit
        await self._check_rate_limit()
        
        # Build payload
        payload = {
            "To": f"whatsapp:{to_formatted}",
            "From": f"whatsapp:{from_formatted}",
            "Body": body,
        }
        
        if media_url:
            payload["MediaUrl"] = media_url
        
        # Check if configured (for development)
        if not self.account_sid or self.account_sid == "your_twilio_account_sid":
            logger.warning(f"📱 [DEV] Would send to {to}: {body[:100]}...")
            return {"status": "dev_mode", "to": to, "body": body}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    auth=(self.account_sid, self.auth_token),
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"📱 Message sent to {to}: {body[:50]}...")
                    return {
                        "status": "sent",
                        "sid": result.get("sid"),
                        "to": to,
                    }
                else:
                    error = response.json()
                    logger.error(f"📱 Failed to send to {to}: {error}")
                    return {
                        "status": "error",
                        "error": error,
                    }
                    
        except Exception as e:
            logger.error(f"📱 WhatsApp error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def send_template(
        self,
        to: str,
        template_name: str,
        template_params: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp template message
        
        For pre-approved message templates (required for initiating conversations)
        """
        # Template messages require Twilio Content API
        # For now, fall back to regular message
        logger.warning("Template messages not yet implemented, using regular message")
        
        # Build message from template
        body = self._render_template(template_name, template_params)
        return await self.send_message(to, body)
    
    async def send_bulk(
        self,
        recipients: List[Dict[str, str]],
        body: str,
        delay_ms: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Send message to multiple recipients
        
        Args:
            recipients: List of {phone, name} dicts
            body: Message body (can use {name} placeholder)
            delay_ms: Delay between messages to avoid rate limits
        """
        results = []
        
        for recipient in recipients:
            phone = recipient.get("phone")
            name = recipient.get("name", "")
            
            # Personalize message
            personalized = body.replace("{name}", name)
            
            result = await self.send_message(phone, personalized)
            results.append({**result, "phone": phone, "name": name})
            
            # Small delay between messages
            await asyncio.sleep(delay_ms / 1000)
        
        return results
    
    async def send_welcome(self, phone: str, name: str, role: str, org_name: str) -> Dict[str, Any]:
        """Send welcome message to new user"""
        
        if role in ["owner", "admin"]:
            message = f"""Welcome to SiteMind, {name}! 🎉

You're now set up as {role} for {org_name}.

Your team can send any construction query via WhatsApp and get instant, accurate answers.

To get started:
• Forward any drawing to this number
• Ask any question about the project
• Type 'help' for all commands

Questions? Just reply here!"""
        
        elif role == "pm":
            message = f"""Welcome to SiteMind, {name}!

You've been added as Project Manager for {org_name}.

You can:
• Ask any question about project specs
• Upload documents and photos
• Create and assign tasks
• Manage team members

Quick commands:
• `list team` - See team members
• `add team [name] [phone] [role]` - Add someone
• `help` - All commands

Try it now - send any question!"""
        
        else:  # site_engineer, consultant, viewer
            message = f"""Welcome to SiteMind, {name}!

You've been added to {org_name}'s project team.

I can help you with:
• Blueprint specifications ("beam size B3?")
• Rebar details ("sariya at C4?")
• Material info ("steel grade?")

Just send your question - I respond 24/7!

Type 'help' for all commands.

Try it now: Send any question about the project!"""
        
        return await self.send_message(phone, message)
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _format_number(self, phone: str) -> str:
        """Format phone number for WhatsApp"""
        # Remove any whatsapp: prefix
        phone = phone.replace("whatsapp:", "")
        
        # Remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")
        
        # Ensure + prefix
        if not phone.startswith("+"):
            if phone.startswith("91"):
                phone = f"+{phone}"
            else:
                phone = f"+91{phone}"
        
        return phone
    
    def _render_template(self, template_name: str, params: Dict[str, str]) -> str:
        """Render a message template"""
        templates = {
            "welcome": "Welcome to SiteMind, {name}! You've been added to {project}. Send any question to get started!",
            "drawing_update": "New drawing uploaded: {drawing_name}. Please review and acknowledge.",
            "task_assigned": "New task assigned: {task_name}. Due: {due_date}. Reply 'done' when complete.",
            "red_flag": "⚠️ Alert: {title}\n\n{description}\n\nPlease investigate.",
        }
        
        template = templates.get(template_name, template_name)
        
        for key, value in params.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    async def _check_rate_limit(self):
        """Check and enforce rate limit"""
        now = datetime.utcnow()
        
        # Reset counter every minute
        if (now - self._last_reset).seconds >= 60:
            self._message_count = 0
            self._last_reset = now
        
        # Check limit
        if self._message_count >= self._rate_limit:
            wait_time = 60 - (now - self._last_reset).seconds
            logger.warning(f"Rate limit reached, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
            self._message_count = 0
            self._last_reset = datetime.utcnow()
        
        self._message_count += 1


# Singleton instance
whatsapp_client = WhatsAppClient()
