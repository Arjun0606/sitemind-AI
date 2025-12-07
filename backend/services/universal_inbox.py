"""
SiteMind Universal Inbox Service
Process any input type from any source

SUPPORTED INPUTS:
- Text messages (queries, commands)
- Images (photos, drawings)
- Documents (PDFs, drawings)
- Voice (transcribed to text) - currently disabled

INTENTS:
- Query (asking a question)
- Upload (sharing a document/photo)
- Command (team mgmt, task mgmt)
- Report (status update)
- Greeting
- Acknowledgment
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import re


class InputType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"


class InputIntent(str, Enum):
    QUERY = "query"
    UPLOAD_DOCUMENT = "upload_document"
    UPLOAD_PHOTO = "upload_photo"
    COMMAND = "command"
    REPORT = "report"
    GREETING = "greeting"
    ACKNOWLEDGMENT = "acknowledgment"
    UNKNOWN = "unknown"


class UniversalInboxService:
    """
    Process any type of input from WhatsApp
    """
    
    def __init__(self):
        # Greeting patterns
        self.greeting_patterns = [
            r"^(hi|hello|hey|good morning|good evening|namaste|namaskar)[\s!]*$",
        ]
        
        # Acknowledgment patterns
        self.ack_patterns = [
            r"^(ok|okay|thanks|thank you|got it|understood|thik hai|theek hai|acha|accha|done|haan|ha|ji)[\s!.]*$",
        ]
        
        # Report patterns
        self.report_patterns = [
            r"(today|aaj)\s*(complete|done|finished|khatam)",
            r"(work|kaam)\s*(started|shuru)",
            r"(poured|pour|casting)\s*(complete|done)",
        ]
    
    async def process_input(
        self,
        project_id: str,
        user_id: str,
        user_phone: str,
        message_type: str,
        content: str,
        media_url: Optional[str] = None,
        media_mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process incoming input and classify it
        
        Returns:
            - input_type: What kind of input this is
            - intent: What the user wants to do
            - extracted_data: Any extracted structured data
            - requires_response: Whether we need to respond
        """
        # Determine input type
        if message_type == "image":
            input_type = InputType.IMAGE
        elif message_type == "document":
            input_type = InputType.DOCUMENT
        elif message_type == "audio":
            input_type = InputType.AUDIO
        else:
            input_type = InputType.TEXT
        
        # Classify intent
        intent = self._classify_intent(input_type, content)
        
        # Extract structured data
        extracted = self._extract_data(content, intent)
        
        return {
            "input_type": input_type,
            "intent": intent,
            "extracted_data": extracted,
            "requires_response": intent not in [InputIntent.ACKNOWLEDGMENT],
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def _classify_intent(
        self,
        input_type: InputType,
        content: str,
    ) -> InputIntent:
        """Classify the intent of the input"""
        content_lower = content.lower().strip() if content else ""
        
        # Image/document uploads
        if input_type == InputType.IMAGE:
            return InputIntent.UPLOAD_PHOTO
        
        if input_type == InputType.DOCUMENT:
            return InputIntent.UPLOAD_DOCUMENT
        
        # Text classification
        if not content_lower:
            return InputIntent.UNKNOWN
        
        # Greetings
        for pattern in self.greeting_patterns:
            if re.match(pattern, content_lower, re.IGNORECASE):
                return InputIntent.GREETING
        
        # Acknowledgments
        for pattern in self.ack_patterns:
            if re.match(pattern, content_lower, re.IGNORECASE):
                return InputIntent.ACKNOWLEDGMENT
        
        # Reports
        for pattern in self.report_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return InputIntent.REPORT
        
        # Commands (team, task, material)
        if self._is_command(content_lower):
            return InputIntent.COMMAND
        
        # Default to query
        return InputIntent.QUERY
    
    def _is_command(self, content: str) -> bool:
        """Check if content is a command"""
        command_patterns = [
            r"^add\s+team",
            r"^remove\s+team",
            r"^list\s+team",
            r"^change\s+role",
            r"^task\s+",
            r"^assign\s+",
            r"^done\s+",
            r"^blocked\s+",
            r"^my\s+tasks",
            r"^stock\s+",
            r"^inventory",
            r"^received\s+",
            r"^used\s+",
        ]
        
        for pattern in command_patterns:
            if re.match(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_data(
        self,
        content: str,
        intent: InputIntent,
    ) -> Dict[str, Any]:
        """Extract structured data from content"""
        extracted = {}
        
        if not content:
            return extracted
        
        # Extract location references
        grid_match = re.search(r'\b([A-Z]\d+)\b', content, re.IGNORECASE)
        if grid_match:
            extracted["grid"] = grid_match.group(1).upper()
        
        floor_match = re.search(r'(?:floor|fl|level|manzil)\s*(\d+)', content, re.IGNORECASE)
        if floor_match:
            extracted["floor"] = int(floor_match.group(1))
        
        # Extract element references
        elements = ["beam", "column", "slab", "foundation", "wall", "staircase"]
        for elem in elements:
            if elem in content.lower():
                extracted["element"] = elem
                break
        
        # Extract quantities (for material commands)
        qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(bags?|MT|cum?\.?m|nos?\.?)', content, re.IGNORECASE)
        if qty_match:
            extracted["quantity"] = float(qty_match.group(1))
            extracted["unit"] = qty_match.group(2)
        
        return extracted
    
    def format_classification(self, result: Dict[str, Any]) -> str:
        """Format classification result for logging"""
        return f"""
Input Type: {result['input_type'].value}
Intent: {result['intent'].value}
Extracted: {result['extracted_data']}
Requires Response: {result['requires_response']}
"""


# Singleton instance
universal_inbox = UniversalInboxService()
