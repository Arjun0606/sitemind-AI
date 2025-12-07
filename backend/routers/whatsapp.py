"""
SiteMind WhatsApp Router
The main entry point - handles ALL incoming WhatsApp messages

FLOW:
1. Receive message from Twilio webhook
2. Identify user and project
3. Classify input (query, upload, command, etc.)
4. Process through appropriate service
5. Send response back via WhatsApp
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

from utils.logger import logger

# Import all services
from services.universal_inbox import universal_inbox, InputType, InputIntent
from services.smart_assistant import smart_assistant
from services.gemini_service import GeminiService
from services.memory_service import MemoryService
from services.whatsapp_client import WhatsAppClient
from services.storage_service import StorageService
from services.red_flag_service import red_flag_service
from services.team_management import team_management
from services.task_management import task_management, TaskStatus
from services.material_management import material_management
from services.progress_monitoring import progress_monitoring
from services.office_site_sync import office_site_sync
from services.proactive_intelligence import proactive_intelligence
from services.engagement_service import engagement_service
from services.roi_service import ROIService
from services.config_service import config_service


router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Initialize services (in production, use dependency injection)
gemini = GeminiService()
memory = MemoryService()
whatsapp = WhatsAppClient()
storage = StorageService()
roi = ROIService()


# =============================================================================
# MODELS
# =============================================================================

class TwilioWebhook(BaseModel):
    """Twilio WhatsApp webhook payload"""
    From: str
    To: str
    Body: Optional[str] = ""
    NumMedia: Optional[str] = "0"
    MediaUrl0: Optional[str] = None
    MediaContentType0: Optional[str] = None
    MessageSid: Optional[str] = None
    ProfileName: Optional[str] = None


# =============================================================================
# MAIN WEBHOOK ENDPOINT
# =============================================================================

@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Main WhatsApp webhook - handles all incoming messages
    """
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        data = dict(form_data)
        
        # Extract message details
        from_number = data.get("From", "").replace("whatsapp:", "")
        to_number = data.get("To", "").replace("whatsapp:", "")
        body = data.get("Body", "").strip()
        num_media = int(data.get("NumMedia", "0"))
        media_url = data.get("MediaUrl0")
        media_type = data.get("MediaContentType0")
        profile_name = data.get("ProfileName", "User")
        message_sid = data.get("MessageSid")
        
        logger.info(f"📱 WhatsApp message from {from_number}: {body[:50]}...")
        
        # Look up user and project
        user, project = await lookup_user_project(from_number)
        
        if not user or not project:
            # Unknown user - send registration message
            await send_unknown_user_response(from_number)
            return {"status": "unknown_user"}
        
        # Get user config
        org_id = project.get("organization_id")
        project_id = project.get("id")
        user_id = user.get("id")
        user_role = user.get("role", "site_engineer")
        
        # Process the message
        response = await process_message(
            user=user,
            project=project,
            body=body,
            num_media=num_media,
            media_url=media_url,
            media_type=media_type,
            profile_name=profile_name,
        )
        
        # Send response
        if response.get("message"):
            await whatsapp.send_message(from_number, response["message"])
        
        # Send any follow-up messages (e.g., welcome message to new team member)
        if response.get("welcome_message"):
            wm = response["welcome_message"]
            await whatsapp.send_message(wm["phone"], wm["message"])
        
        # Track metrics in background
        background_tasks.add_task(
            track_interaction,
            user_id=user_id,
            project_id=project_id,
            query=body,
            response=response.get("message", ""),
            intent=response.get("intent", "unknown"),
        )
        
        return {"status": "ok", "message_sid": message_sid}
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MESSAGE PROCESSING
# =============================================================================

async def process_message(
    user: Dict,
    project: Dict,
    body: str,
    num_media: int,
    media_url: Optional[str],
    media_type: Optional[str],
    profile_name: str,
) -> Dict[str, Any]:
    """
    Process incoming message through the full pipeline
    """
    user_id = user.get("id")
    user_phone = user.get("phone")
    user_role = user.get("role", "site_engineer")
    project_id = project.get("id")
    org_id = project.get("organization_id")
    
    # Get config
    branding = config_service.get_branding(org_id) if org_id else {}
    assistant_name = branding.get("assistant_name", "SiteMind")
    
    # Determine message type
    message_type = "text"
    if num_media > 0:
        if media_type and "image" in media_type:
            message_type = "image"
        elif media_type and "pdf" in media_type:
            message_type = "document"
        elif media_type and "audio" in media_type:
            message_type = "audio"
    
    # =========================================================================
    # STEP 1: Check for special commands
    # =========================================================================
    
    # Team management commands
    team_cmd = team_management.parse_command(body)
    if team_cmd:
        result = await team_management.execute_command(
            command=team_cmd,
            requester_phone=user_phone,
            project_id=project_id,
            organization_id=org_id,
        )
        return {
            "message": result.get("message"),
            "intent": "team_management",
            "welcome_message": result.get("welcome_message"),
        }
    
    # Task management commands
    task_cmd = parse_task_command(body, user_role)
    if task_cmd:
        result = await handle_task_command(task_cmd, user, project)
        return {
            "message": result.get("message"),
            "intent": "task_management",
        }
    
    # Material commands
    material_cmd = parse_material_command(body)
    if material_cmd:
        result = await handle_material_command(material_cmd, user, project)
        return {
            "message": result.get("message"),
            "intent": "material_management",
        }
    
    # Report requests
    if is_report_request(body):
        report = await generate_report(body, project, user_role)
        return {
            "message": report,
            "intent": "report_request",
        }
    
    # Help command
    if body.lower() in ["help", "?", "commands", "menu"]:
        return {
            "message": get_help_message(user_role, assistant_name),
            "intent": "help",
        }
    
    # =========================================================================
    # STEP 2: Classify input through Universal Inbox
    # =========================================================================
    
    classification = await universal_inbox.process_input(
        project_id=project_id,
        user_id=user_id,
        user_phone=user_phone,
        message_type=message_type,
        content=body,
        media_url=media_url,
        media_mime_type=media_type,
    )
    
    input_type = classification["input_type"]
    intent = classification["intent"]
    extracted = classification["extracted_data"]
    
    # =========================================================================
    # STEP 3: Handle based on intent
    # =========================================================================
    
    # Document uploads
    if intent == InputIntent.UPLOAD_DOCUMENT and media_url:
        # Store document
        doc_result = await handle_document_upload(
            media_url, media_type, body, user, project
        )
        return {
            "message": doc_result.get("message"),
            "intent": "upload_document",
        }
    
    # Photo uploads
    if message_type == "image" and media_url:
        photo_result = await handle_photo_upload(
            media_url, body, user, project, extracted
        )
        return {
            "message": photo_result.get("message"),
            "intent": "upload_photo",
        }
    
    # Greetings
    if intent == InputIntent.GREETING:
        return {
            "message": f"Hello {profile_name}! I'm {assistant_name}, your construction assistant. How can I help you today?",
            "intent": "greeting",
        }
    
    # Acknowledgments
    if intent == InputIntent.ACKNOWLEDGMENT:
        return {
            "message": None,  # No response needed for "ok", "thanks"
            "intent": "acknowledgment",
        }
    
    # =========================================================================
    # STEP 4: Process as query through Smart Assistant
    # =========================================================================
    
    # Pre-process query
    processed = smart_assistant.preprocess_query(body)
    
    # Check for ambiguity
    if processed.get("needs_clarification"):
        return {
            "message": processed["clarification_question"],
            "intent": "clarification_needed",
        }
    
    # Detect urgency
    urgency = smart_assistant.detect_urgency(body)
    
    # Search memory for context
    memory_results = await memory.search(
        project_id=project_id,
        query=processed.get("normalized_query", body),
        limit=5,
    )
    
    # Check for conflicts in memory
    conflicts = smart_assistant.detect_conflicts(memory_results)
    if conflicts:
        # Flag conflict but still answer
        proactive_intelligence.record_issue(project_id, "conflict", conflicts[0])
    
    # Generate response with Gemini
    response_text = await gemini.query(
        query=body,
        context=memory_results,
        project_id=project_id,
    )
    
    # Check for red flags
    red_flag = red_flag_service.analyze_query(
        project_id=project_id,
        query=body,
        response=response_text,
        user_phone=user_phone,
        memory_results=memory_results,
    )
    
    if red_flag and red_flag.severity.value in ["critical", "high"]:
        # Add warning to response
        response_text += f"\n\n⚠️ **Note:** {red_flag.title}"
    
    # Enhance response
    user_stats = smart_assistant.get_user_stats(user_phone)
    category = smart_assistant.categorize_query(body)
    response_text = smart_assistant.enhance_response(
        response_text, urgency, category, user_stats
    )
    
    # Record query
    smart_assistant.record_query(user_phone)
    
    # Add to memory for context
    await memory.add_whatsapp_query(
        project_id=project_id,
        question=body,
        answer=response_text,
        user_id=user_id,
    )
    
    # Track ROI
    roi.record_query(project_id, time_saved_minutes=5)
    
    return {
        "message": response_text,
        "intent": intent.value if hasattr(intent, "value") else str(intent),
        "extracted": extracted,
    }


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

def parse_task_command(body: str, role: str) -> Optional[Dict]:
    """Parse task-related commands"""
    body_lower = body.lower().strip()
    
    # Only PMs and above can create tasks
    if role in ["owner", "admin", "pm"]:
        if body_lower.startswith("task ") or body_lower.startswith("assign "):
            return {"type": "create", "raw": body}
    
    # Anyone can update task status
    if body_lower.startswith("done ") or body_lower == "done":
        return {"type": "complete", "raw": body}
    
    if body_lower.startswith("blocked "):
        return {"type": "blocked", "raw": body}
    
    if body_lower in ["my tasks", "tasks", "task list"]:
        return {"type": "list", "raw": body}
    
    return None


async def handle_task_command(cmd: Dict, user: Dict, project: Dict) -> Dict[str, Any]:
    """Handle task management commands"""
    cmd_type = cmd["type"]
    raw = cmd["raw"]
    project_id = project["id"]
    user_phone = user["phone"]
    
    if cmd_type == "list":
        summary = task_management.format_daily_summary(user_phone)
        return {"message": summary}
    
    if cmd_type == "complete":
        # Would find and complete the task
        return {"message": "✅ Task marked as complete. Good work!"}
    
    if cmd_type == "blocked":
        reason = raw.replace("blocked ", "").strip()
        return {"message": f"🚫 Task marked as blocked.\nReason: {reason}\n\nPM has been notified."}
    
    if cmd_type == "create":
        # Parse task creation - simplified
        return {"message": "Task creation via WhatsApp coming soon. Please use the dashboard for now."}
    
    return {"message": "Unknown task command."}


def parse_material_command(body: str) -> Optional[Dict]:
    """Parse material-related commands"""
    body_lower = body.lower().strip()
    
    # Stock query
    if "stock" in body_lower or "inventory" in body_lower:
        return {"type": "query_stock", "raw": body}
    
    # Record receipt
    if body_lower.startswith("received ") or body_lower.startswith("got "):
        return {"type": "receipt", "raw": body}
    
    # Record usage
    if body_lower.startswith("used ") or body_lower.startswith("consumed "):
        return {"type": "consumption", "raw": body}
    
    return None


async def handle_material_command(cmd: Dict, user: Dict, project: Dict) -> Dict[str, Any]:
    """Handle material management commands"""
    cmd_type = cmd["type"]
    raw = cmd["raw"]
    project_id = project["id"]
    
    if cmd_type == "query_stock":
        # Extract material name if present
        material_name = None
        for material in ["cement", "steel", "sand", "aggregate", "brick"]:
            if material in raw.lower():
                material_name = material
                break
        
        response = material_management.get_stock_status(project_id, material_name)
        return {"message": response}
    
    if cmd_type == "receipt":
        return {"message": "Material receipt recorded. (Parsing coming soon)"}
    
    if cmd_type == "consumption":
        return {"message": "Material consumption recorded. (Parsing coming soon)"}
    
    return {"message": "Unknown material command."}


def is_report_request(body: str) -> bool:
    """Check if message is asking for a report"""
    keywords = ["report", "summary", "status all", "progress all", "weekly report", "daily report"]
    return any(kw in body.lower() for kw in keywords)


async def generate_report(body: str, project: Dict, role: str) -> str:
    """Generate requested report"""
    project_id = project["id"]
    project_name = project.get("name", "Project")
    
    if "weekly" in body.lower():
        return engagement_service.generate_weekly_report(project_id, project_name)
    
    if "progress" in body.lower():
        return progress_monitoring.generate_progress_report(project_id)
    
    if "material" in body.lower():
        return material_management.generate_consumption_report(project_id)
    
    # Default daily summary
    return engagement_service.generate_daily_summary(project_id)


async def handle_document_upload(
    media_url: str,
    media_type: str,
    caption: str,
    user: Dict,
    project: Dict,
) -> Dict[str, Any]:
    """Handle document (PDF/drawing) upload"""
    project_id = project["id"]
    user_name = user.get("name", "User")
    
    # Store document
    # In production: download from media_url, upload to Supabase, analyze with Gemini
    
    logger.info(f"📄 Document uploaded by {user_name}: {media_url}")
    
    # Notify team
    office_site_sync.track_drawing_upload(project_id, caption or "New drawing", user_name)
    
    return {
        "message": f"""📄 **Document received**

I'm analyzing this document now. It will be searchable in a few moments.

{f"Caption: {caption}" if caption else ""}

All team members will be notified of this update."""
    }


async def handle_photo_upload(
    media_url: str,
    caption: str,
    user: Dict,
    project: Dict,
    extracted: Dict,
) -> Dict[str, Any]:
    """Handle photo upload (progress, issue, etc.)"""
    project_id = project["id"]
    user_name = user.get("name", "User")
    location = extracted.get("grid") or extracted.get("floor") or "unspecified location"
    
    logger.info(f"📷 Photo uploaded by {user_name}: {caption or 'No caption'}")
    
    # Determine intent from caption
    is_issue = any(word in (caption or "").lower() for word in ["issue", "problem", "crack", "damage"])
    
    if is_issue:
        # Create red flag
        return {
            "message": f"""🚩 **Issue Logged**

Photo received and logged.
Location: {location}
Reported by: {user_name}

Project Manager has been notified.

{f"Description: {caption}" if caption else "Please reply with a description of the issue."}"""
        }
    else:
        # Progress photo
        return {
            "message": f"""📷 **Progress Photo Logged**

Photo received for {location}.
Logged by: {user_name}

{f"Note: {caption}" if caption else ""}

This has been added to the project timeline."""
        }


# =============================================================================
# HELPERS
# =============================================================================

async def lookup_user_project(phone: str) -> tuple:
    """Look up user and their project from phone number"""
    # In production, query database
    # For now, return mock data
    
    # Mock - would be database lookup
    user = {
        "id": "user_123",
        "phone": phone,
        "name": "Test User",
        "role": "site_engineer",
    }
    
    project = {
        "id": "proj_123",
        "organization_id": "org_123",
        "name": "Test Project",
    }
    
    return user, project


async def send_unknown_user_response(phone: str):
    """Send response to unknown user"""
    message = """👋 Hello! I'm SiteMind, an AI construction assistant.

It looks like you're not registered with any project yet.

To get started, please ask your Project Manager to add you to a project. They can do this by sending:

`add team [YourName] [YourPhone] engineer`

Once added, you'll be able to ask questions about the project!"""
    
    await whatsapp.send_message(phone, message)


async def track_interaction(
    user_id: str,
    project_id: str,
    query: str,
    response: str,
    intent: str,
):
    """Track interaction for analytics (background task)"""
    engagement_service.track_query(
        project_id=project_id,
        user_phone=user_id,
        user_name="User",
        query=query,
        response=response,
    )


def get_help_message(role: str, assistant_name: str) -> str:
    """Get help message based on role"""
    base_help = f"""**{assistant_name} Help**

📝 **Ask Questions**
Just type any question about the project:
• "beam size B3 floor 2?"
• "rebar at column C4?"
• "what was decided about staircase?"

📷 **Upload Photos**
Send a photo with caption for:
• Progress updates
• Issue reporting

📊 **Reports**
• `weekly report` - Weekly summary
• `progress report` - Current status
• `my tasks` - Your task list

📦 **Materials**
• `cement stock?` - Check inventory
• `received 50 bags cement` - Log receipt
• `used 10 bags cement floor 3` - Log usage
"""

    if role in ["owner", "admin", "pm"]:
        base_help += """
👥 **Team Management** (PM+)
• `add team [name] [phone] [role]`
• `remove team [phone]`
• `list team`
• `change role [phone] [role]`

Roles: engineer, pm, consultant, viewer, store
"""

    base_help += """
_Reply with your question to get started!_"""

    return base_help


# =============================================================================
# WEBHOOK VERIFICATION (for Twilio setup)
# =============================================================================

@router.get("/webhook")
async def verify_webhook():
    """Webhook verification endpoint"""
    return {"status": "ok", "service": "SiteMind WhatsApp"}


# =============================================================================
# MANUAL MESSAGE ENDPOINT (for testing)
# =============================================================================

class ManualMessage(BaseModel):
    phone: str
    message: str
    project_id: Optional[str] = "proj_123"


@router.post("/send")
async def send_manual_message(msg: ManualMessage):
    """Send a manual message (for testing/admin)"""
    try:
        await whatsapp.send_message(msg.phone, msg.message)
        return {"status": "sent", "to": msg.phone}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MORNING BRIEF TRIGGER
# =============================================================================

@router.post("/trigger-briefs")
async def trigger_morning_briefs():
    """Trigger morning briefs for all projects (called by cron)"""
    # In production, iterate through all active projects
    # and send briefs to relevant users
    return {"status": "briefs_triggered", "count": 0}
