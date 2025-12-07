"""
SiteMind WhatsApp Service
Send and receive messages via Twilio WhatsApp API

SETUP:
1. Create Twilio account at twilio.com
2. Set up WhatsApp sandbox in console
3. Add API keys to .env
"""

from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import settings
from utils.logger import logger


class WhatsAppService:
    """
    Twilio WhatsApp integration
    """
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        
        self._client = None
    
    def _is_configured(self) -> bool:
        """Check if Twilio is configured"""
        return (
            self.account_sid and
            self.account_sid != "your_twilio_account_sid" and
            len(self.account_sid) > 10
        )
    
    @property
    def client(self) -> Optional[Client]:
        """Lazy load Twilio client"""
        if not self._is_configured():
            return None
        
        if not self._client:
            self._client = Client(self.account_sid, self.auth_token)
        
        return self._client
    
    # =========================================================================
    # SEND MESSAGES
    # =========================================================================
    
    async def send_message(
        self,
        to: str,
        body: str,
        media_url: str = None,
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message
        
        Args:
            to: Phone number (with country code)
            body: Message text
            media_url: Optional media URL
        """
        if not self._is_configured():
            logger.warning(f"WhatsApp not configured. Would send: {body[:50]}...")
            return {
                "status": "not_configured",
                "message": body,
            }
        
        # Ensure proper format
        to_number = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        
        try:
            message_params = {
                "from_": self.from_number,
                "to": to_number,
                "body": body,
            }
            
            if media_url:
                message_params["media_url"] = [media_url]
            
            message = self.client.messages.create(**message_params)
            
            logger.info(f"📤 WhatsApp sent to {to}: {body[:50]}...")
            
            return {
                "status": "sent",
                "sid": message.sid,
                "to": to,
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    # =========================================================================
    # FORMATTED MESSAGES
    # =========================================================================
    
    async def send_welcome(self, to: str, user_name: str) -> Dict[str, Any]:
        """Send welcome message to new user"""
        body = f"""🏗️ *Welcome to SiteMind, {user_name}!*

I'm your AI construction assistant. I can help you with:

📐 *Blueprint questions* - Ask about specs, dimensions, materials
📸 *Photo analysis* - Send site photos for quality checks
📄 *Document review* - Share drawings for analysis
🔍 *Code verification* - Check against IS standards
⚠️ *Safety checks* - Flag potential issues

Just send me a message anytime!

_Type "help" for more options_"""
        
        return await self.send_message(to, body)
    
    async def send_answer(
        self,
        to: str,
        question: str,
        answer: str,
    ) -> Dict[str, Any]:
        """Send formatted answer"""
        # Truncate if too long for WhatsApp
        if len(answer) > 1500:
            answer = answer[:1500] + "\n\n_(Response truncated. Ask for more details.)_"
        
        body = f"""*Q:* {question}

{answer}

---
_Reply with follow-up questions_"""
        
        return await self.send_message(to, body)
    
    async def send_analysis(
        self,
        to: str,
        analysis_type: str,
        analysis: str,
    ) -> Dict[str, Any]:
        """Send image/document analysis"""
        type_labels = {
            "image": "📸 Image Analysis",
            "document": "📄 Document Analysis",
            "photo": "📸 Photo Analysis",
            "blueprint": "📐 Blueprint Analysis",
        }
        
        label = type_labels.get(analysis_type, "🔍 Analysis")
        
        body = f"""*{label}*

{analysis}

---
_Ask follow-up questions or send more files_"""
        
        return await self.send_message(to, body)
    
    async def send_alert(
        self,
        to: str,
        alert_type: str,
        message: str,
    ) -> Dict[str, Any]:
        """Send alert/notification"""
        type_icons = {
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            "info": "ℹ️",
            "urgent": "🚨",
        }
        
        icon = type_icons.get(alert_type, "ℹ️")
        
        body = f"""{icon} *{alert_type.upper()}*

{message}"""
        
        return await self.send_message(to, body)
    
    async def send_daily_brief(
        self,
        to: str,
        project_name: str,
        summary: str,
    ) -> Dict[str, Any]:
        """Send daily project brief"""
        body = f"""☀️ *Good Morning!*

*Project:* {project_name}

{summary}

---
_Have a productive day!_"""
        
        return await self.send_message(to, body)
    
    async def send_help(self, to: str) -> Dict[str, Any]:
        """Send help message"""
        body = """🏗️ *SiteMind Help*

*Commands:*
• _help_ - Show this message
• _status_ - Project status
• _team_ - List team members

*Ask Me:*
• Construction questions
• Material specifications
• Code references (IS, NBC)
• Quality checks

*Send Me:*
• 📸 Photos - For site analysis
• 📄 Documents - For review
• 📐 Drawings - For specifications

*Examples:*
• "What's the minimum cover for RCC columns?"
• "Check if 12mm bar spacing is correct"
• "Analyze this concrete pour photo"

---
_Just type your question!_"""
        
        return await self.send_message(to, body)
    
    # =========================================================================
    # PARSE INCOMING
    # =========================================================================
    
    def parse_incoming(self, data: Dict) -> Dict[str, Any]:
        """
        Parse incoming webhook data from Twilio
        
        Returns structured message data
        """
        return {
            "from": data.get("From", "").replace("whatsapp:", ""),
            "to": data.get("To", "").replace("whatsapp:", ""),
            "body": data.get("Body", "").strip(),
            "num_media": int(data.get("NumMedia", 0)),
            "media_urls": [
                data.get(f"MediaUrl{i}")
                for i in range(int(data.get("NumMedia", 0)))
            ],
            "media_types": [
                data.get(f"MediaContentType{i}")
                for i in range(int(data.get("NumMedia", 0)))
            ],
            "message_sid": data.get("MessageSid"),
            "account_sid": data.get("AccountSid"),
            "profile_name": data.get("ProfileName"),
        }


# Singleton instance
whatsapp_service = WhatsAppService()

