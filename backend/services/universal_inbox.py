"""
SiteMind Universal Inbox
The magic entry point - forward ANYTHING to SiteMind, it understands

SUPPORTED INPUTS:
- Text queries (any language)
- PDF drawings
- Images (photos, screenshots, drawings)
- Voice notes (transcribed)
- Forwarded messages
- Photos of handwritten notes
- Screenshots of emails
- Location pins

Every input is:
1. Classified (what type is this?)
2. Processed (extract information)
3. Stored (add to project memory)
4. Responded (answer if needed)
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import re

from utils.logger import logger


class InputType(str, Enum):
    # Text
    TEXT_QUERY = "text_query"           # "beam size B3?"
    TEXT_INSTRUCTION = "text_instruction"  # "change beam to 300x600"
    TEXT_DECISION = "text_decision"     # "approved by client"
    TEXT_UPDATE = "text_update"         # "Floor 3 complete"
    
    # Documents
    DOC_DRAWING = "doc_drawing"         # PDF/DWG drawing
    DOC_SPECIFICATION = "doc_specification"
    DOC_RFI = "doc_rfi"
    DOC_CHANGE_ORDER = "doc_change_order"
    DOC_OTHER = "doc_other"
    
    # Images
    IMG_SITE_PHOTO = "img_site_photo"   # Progress/issue photo
    IMG_DRAWING = "img_drawing"         # Photo of drawing
    IMG_SCREENSHOT = "img_screenshot"   # Screenshot of chat/email
    IMG_HANDWRITTEN = "img_handwritten" # Photo of handwritten note
    IMG_OTHER = "img_other"
    
    # Audio
    AUDIO_QUERY = "audio_query"         # Voice question
    AUDIO_INSTRUCTION = "audio_instruction"
    
    # Other
    LOCATION = "location"               # GPS pin
    CONTACT = "contact"                 # Shared contact
    FORWARDED = "forwarded"             # Forwarded message
    UNKNOWN = "unknown"


class InputIntent(str, Enum):
    """What does the user want?"""
    ASK_QUESTION = "ask_question"       # Wants information
    UPLOAD_DOCUMENT = "upload_document" # Sharing a document
    REPORT_PROGRESS = "report_progress" # Status update
    REPORT_ISSUE = "report_issue"       # Problem/concern
    LOG_DECISION = "log_decision"       # Record a decision
    CREATE_TASK = "create_task"         # Assign work
    UPDATE_TASK = "update_task"         # Task status change
    REQUEST_REPORT = "request_report"   # Want a summary
    RECORD_MATERIAL = "record_material" # Material transaction
    GREETING = "greeting"               # Hello, hi
    ACKNOWLEDGMENT = "acknowledgment"   # Ok, thanks
    OTHER = "other"


class UniversalInboxService:
    """
    Processes any input from WhatsApp
    """
    
    def __init__(self):
        # Query patterns
        self.query_patterns = [
            r"(kya|what|kitna|how much|size|dimension|spec)",
            r"\?$",
            r"(batao|bolo|tell|show)",
            r"(beam|column|slab|rebar|sariya|khamba)",
        ]
        
        # Decision patterns
        self.decision_patterns = [
            r"(approved|rejected|decided|confirmed|finalized)",
            r"(client|architect|consultant|MD|owner).*said",
            r"(go ahead|proceed|stop|cancel)",
        ]
        
        # Progress patterns
        self.progress_patterns = [
            r"(complete|done|finished|started|in progress)",
            r"(\d+%|percent)",
            r"(poured|casted|fixed|installed)",
        ]
        
        # Issue patterns
        self.issue_patterns = [
            r"(problem|issue|crack|leak|damage|wrong)",
            r"(urgent|jaldi|abhi|emergency)",
            r"(not matching|doesn't match|mismatch)",
        ]
        
        # Material patterns
        self.material_patterns = [
            r"(received|used|consumed|remaining|stock)",
            r"(bags|MT|pieces|kg|rods)",
            r"(cement|steel|sand|aggregate|brick)",
        ]
    
    async def process_input(
        self,
        project_id: str,
        user_id: str,
        user_phone: str,
        message_type: str,  # text, image, document, audio, location
        content: str = None,
        media_url: str = None,
        media_mime_type: str = None,
        forwarded: bool = False,
        caption: str = None,
    ) -> Dict[str, Any]:
        """
        Process any input and return classification + next action
        """
        result = {
            "input_type": InputType.UNKNOWN,
            "intent": InputIntent.OTHER,
            "extracted_data": {},
            "should_respond": True,
            "should_store": True,
            "response": None,
            "actions": [],
        }
        
        # Classify input type
        result["input_type"] = self._classify_input_type(
            message_type, content, media_mime_type, forwarded
        )
        
        # Detect intent
        result["intent"] = self._detect_intent(
            result["input_type"], content, caption
        )
        
        # Extract entities
        result["extracted_data"] = self._extract_entities(
            content or caption or ""
        )
        
        # Determine actions
        result["actions"] = self._determine_actions(
            result["input_type"],
            result["intent"],
        )
        
        # Generate immediate response (if needed)
        result["response"] = self._generate_immediate_response(
            result["input_type"],
            result["intent"],
        )
        
        logger.info(f"📥 Input classified: {result['input_type'].value} | Intent: {result['intent'].value}")
        
        return result
    
    def _classify_input_type(
        self,
        message_type: str,
        content: str,
        mime_type: str,
        forwarded: bool,
    ) -> InputType:
        """Classify what type of input this is"""
        
        if forwarded:
            return InputType.FORWARDED
        
        if message_type == "text":
            content_lower = (content or "").lower()
            
            # Check for decision
            if any(re.search(p, content_lower) for p in self.decision_patterns):
                return InputType.TEXT_DECISION
            
            # Check for progress update
            if any(re.search(p, content_lower) for p in self.progress_patterns):
                return InputType.TEXT_UPDATE
            
            # Check for instruction/change
            if any(word in content_lower for word in ["change", "modify", "update", "badlo"]):
                return InputType.TEXT_INSTRUCTION
            
            # Default to query
            return InputType.TEXT_QUERY
        
        elif message_type == "image":
            # Would use AI to classify image type
            # For now, default to site photo
            return InputType.IMG_SITE_PHOTO
        
        elif message_type == "document":
            if mime_type:
                if "pdf" in mime_type:
                    return InputType.DOC_DRAWING
                elif "dwg" in mime_type or "autocad" in mime_type:
                    return InputType.DOC_DRAWING
            return InputType.DOC_OTHER
        
        elif message_type == "audio":
            return InputType.AUDIO_QUERY
        
        elif message_type == "location":
            return InputType.LOCATION
        
        return InputType.UNKNOWN
    
    def _detect_intent(
        self,
        input_type: InputType,
        content: str,
        caption: str,
    ) -> InputIntent:
        """Detect what the user wants"""
        
        text = (content or caption or "").lower()
        
        # Greeting
        if any(g in text for g in ["hi", "hello", "hey", "namaste", "good morning"]):
            if len(text.split()) <= 3:
                return InputIntent.GREETING
        
        # Acknowledgment
        if any(a in text for a in ["ok", "okay", "thanks", "thank you", "dhanyavad", "got it"]):
            if len(text.split()) <= 4:
                return InputIntent.ACKNOWLEDGMENT
        
        # Document upload
        if input_type in [InputType.DOC_DRAWING, InputType.DOC_SPECIFICATION, 
                          InputType.DOC_RFI, InputType.DOC_CHANGE_ORDER]:
            return InputIntent.UPLOAD_DOCUMENT
        
        # Photo-based intents
        if input_type == InputType.IMG_SITE_PHOTO:
            if any(p in text for p in ["progress", "done", "complete", "update"]):
                return InputIntent.REPORT_PROGRESS
            if any(p in text for p in ["issue", "problem", "crack", "damage"]):
                return InputIntent.REPORT_ISSUE
            return InputIntent.REPORT_PROGRESS  # Default for photos
        
        # Text-based intents
        if input_type == InputType.TEXT_QUERY:
            if "?" in text or any(re.search(p, text) for p in self.query_patterns):
                return InputIntent.ASK_QUESTION
        
        if input_type == InputType.TEXT_DECISION:
            return InputIntent.LOG_DECISION
        
        if input_type == InputType.TEXT_UPDATE:
            return InputIntent.REPORT_PROGRESS
        
        # Material
        if any(re.search(p, text) for p in self.material_patterns):
            return InputIntent.RECORD_MATERIAL
        
        # Task
        if any(t in text for t in ["task", "assign", "todo"]):
            return InputIntent.CREATE_TASK
        if any(t in text for t in ["done", "completed", "finished", "blocked"]):
            return InputIntent.UPDATE_TASK
        
        # Report request
        if any(r in text for r in ["report", "summary", "status all", "progress all"]):
            return InputIntent.REQUEST_REPORT
        
        # Default: treat as question
        return InputIntent.ASK_QUESTION
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract structured entities from text"""
        
        entities = {}
        text_lower = text.lower()
        
        # Location (Grid reference)
        grid_match = re.search(r'\b([A-Z]\d+)\b', text, re.IGNORECASE)
        if grid_match:
            entities["grid"] = grid_match.group(1).upper()
        
        # Floor
        floor_match = re.search(r'(?:floor|fl|level|lvl|manzil)\s*(\d+)', text_lower)
        if floor_match:
            entities["floor"] = int(floor_match.group(1))
        
        # Structural element
        elements = {
            "beam": ["beam", "beem", "girder"],
            "column": ["column", "colum", "khamba", "pillar"],
            "slab": ["slab", "chhat", "roof"],
            "foundation": ["foundation", "footing", "neev", "buniyad"],
            "wall": ["wall", "deewar"],
            "staircase": ["staircase", "stair", "seedi"],
        }
        for elem, patterns in elements.items():
            if any(p in text_lower for p in patterns):
                entities["element"] = elem
                break
        
        # Dimensions
        dim_match = re.search(r'(\d+)\s*[xX×]\s*(\d+)', text)
        if dim_match:
            entities["dimensions"] = f"{dim_match.group(1)}x{dim_match.group(2)}"
        
        # Percentage
        pct_match = re.search(r'(\d+)\s*%', text)
        if pct_match:
            entities["percentage"] = int(pct_match.group(1))
        
        # Material quantities
        qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(bags?|MT|kg|pieces?|nos?|rods?)', text_lower)
        if qty_match:
            entities["quantity"] = {
                "value": float(qty_match.group(1)),
                "unit": qty_match.group(2),
            }
        
        # Urgency
        if any(u in text_lower for u in ["urgent", "jaldi", "abhi", "immediately", "asap"]):
            entities["urgency"] = "high"
        
        return entities
    
    def _determine_actions(
        self,
        input_type: InputType,
        intent: InputIntent,
    ) -> List[str]:
        """Determine what actions to take"""
        
        actions = []
        
        # Document uploads
        if intent == InputIntent.UPLOAD_DOCUMENT:
            actions.append("store_document")
            actions.append("analyze_with_ai")
            actions.append("add_to_memory")
            actions.append("notify_team")
        
        # Questions
        elif intent == InputIntent.ASK_QUESTION:
            actions.append("search_memory")
            actions.append("search_documents")
            actions.append("generate_response")
            actions.append("log_query")
        
        # Progress updates
        elif intent == InputIntent.REPORT_PROGRESS:
            actions.append("log_progress")
            actions.append("update_milestone")
            if input_type == InputType.IMG_SITE_PHOTO:
                actions.append("analyze_photo")
        
        # Issues
        elif intent == InputIntent.REPORT_ISSUE:
            actions.append("create_red_flag")
            actions.append("notify_pm")
            actions.append("log_issue")
        
        # Decisions
        elif intent == InputIntent.LOG_DECISION:
            actions.append("add_to_memory")
            actions.append("create_audit_entry")
            actions.append("notify_relevant_parties")
        
        # Material
        elif intent == InputIntent.RECORD_MATERIAL:
            actions.append("update_inventory")
            actions.append("check_stock_levels")
        
        # Tasks
        elif intent == InputIntent.CREATE_TASK:
            actions.append("create_task")
            actions.append("notify_assignee")
        elif intent == InputIntent.UPDATE_TASK:
            actions.append("update_task_status")
        
        # Reports
        elif intent == InputIntent.REQUEST_REPORT:
            actions.append("generate_report")
        
        return actions
    
    def _generate_immediate_response(
        self,
        input_type: InputType,
        intent: InputIntent,
    ) -> Optional[str]:
        """Generate immediate acknowledgment if needed"""
        
        if intent == InputIntent.GREETING:
            return "Hello! I'm SiteMind, your AI construction assistant. How can I help today?"
        
        if intent == InputIntent.ACKNOWLEDGMENT:
            return None  # No response needed
        
        if intent == InputIntent.UPLOAD_DOCUMENT:
            return "Document received. Analyzing and adding to project memory..."
        
        if intent == InputIntent.REPORT_PROGRESS:
            return "Progress update noted. Logging to project records."
        
        if intent == InputIntent.REPORT_ISSUE:
            return "Issue noted. Creating alert and notifying project manager."
        
        if intent == InputIntent.LOG_DECISION:
            return "Decision recorded with timestamp. Added to project audit trail."
        
        if intent == InputIntent.RECORD_MATERIAL:
            return "Processing material update..."
        
        # For questions, we generate response after searching
        return None
    
    # =========================================================================
    # SPECIALIZED PROCESSORS
    # =========================================================================
    
    async def process_drawing(
        self,
        project_id: str,
        file_url: str,
        file_name: str,
        uploaded_by: str,
    ) -> Dict[str, Any]:
        """Process an uploaded drawing"""
        return {
            "action": "Drawing processing",
            "steps": [
                "1. Store in Supabase",
                "2. Extract with Gemini (text, dimensions, specs)",
                "3. Create searchable memory entries",
                "4. Notify team of new drawing",
            ],
            "file": file_name,
        }
    
    async def process_site_photo(
        self,
        project_id: str,
        photo_url: str,
        caption: str,
        uploaded_by: str,
    ) -> Dict[str, Any]:
        """Process a site photo"""
        return {
            "action": "Photo processing",
            "steps": [
                "1. Store in Supabase",
                "2. Analyze with Gemini (detect work stage, quality)",
                "3. Update progress if applicable",
                "4. Flag issues if detected",
            ],
            "caption": caption,
        }
    
    async def process_voice_note(
        self,
        project_id: str,
        audio_url: str,
        user_phone: str,
    ) -> Dict[str, Any]:
        """Process a voice note"""
        return {
            "action": "Voice processing",
            "steps": [
                "1. Transcribe with Gemini",
                "2. Classify intent",
                "3. Process as text query",
            ],
        }


# Singleton instance
universal_inbox = UniversalInboxService()

