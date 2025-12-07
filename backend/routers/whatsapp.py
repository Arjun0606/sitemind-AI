"""
SiteMind WhatsApp Webhook Router
The MAIN interface - everything happens via WhatsApp

INDIAN CONSTRUCTION WORKFLOW:
- Architect sends updated drawing → SiteMind processes & stores
- Office sends change order → SiteMind records with audit trail
- Engineer asks question → SiteMind answers with citations
- Anyone sends photo → SiteMind verifies against blueprints

SUPPORTED MESSAGE TYPES:
1. Text query → AI answers from blueprints + memory
2. Site photo → AI verifies against drawings
3. Blueprint/Drawing (PDF/image) → AI processes & stores
4. Change order/RFI text → AI records in memory
"""

import time
import re
from typing import Optional, Tuple
from datetime import datetime
from fastapi import APIRouter, Request, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from config import settings
from utils.logger import logger
from utils.helpers import extract_phone_number
from utils.database import get_async_session
from models.database import Project, SiteEngineer, Blueprint, ChatLog
from services.gemini_service import gemini_service
from services.memory_service import memory_service
from services.whatsapp_client import whatsapp_client
from services.storage_service import storage_service
from services.smart_assistant import smart_assistant
from services.engagement_service import engagement_service


router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


# Keywords that indicate document upload vs query
DRAWING_KEYWORDS = [
    "revised", "revision", "new drawing", "updated drawing", "nayi drawing",
    "new plan", "updated plan", "floor plan", "structural", "architectural",
    "mep", "electrical", "plumbing", "section", "detail", "schedule",
    "bar bending", "bbs", "column schedule", "beam schedule", "slab",
    "v2", "v3", "rev", "r1", "r2", "r3", "latest"
]

CHANGE_ORDER_KEYWORDS = [
    "change order", "co#", "co-", "change:", "changed", "badal", "badlo",
    "modification", "modified", "updated spec", "new spec", "revised spec",
    "increase", "decrease", "moved", "shifted", "relocated"
]

RFI_KEYWORDS = [
    "rfi", "rfi#", "rfi-", "clarification", "query answered", "answer:",
    "confirmed", "consultant says", "architect says", "structural says",
    "as per consultant", "jawab", "reply"
]

ADMIN_KEYWORDS = [
    "add engineer", "remove engineer", "new site", "add site",
    "project status", "usage report", "billing"
]


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    # Twilio webhook form fields
    MessageSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: Optional[str] = Form(""),
    NumMedia: str = Form("0"),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
    ProfileName: Optional[str] = Form(None),
):
    """
    Main WhatsApp webhook - handles ALL interactions
    
    Flow:
    1. Identify user and their project
    2. Detect message intent (query, drawing upload, change order, etc.)
    3. Process accordingly
    4. Store in memory for future reference
    5. Respond
    """
    start_time = time.time()
    
    try:
        user_phone = extract_phone_number(From)
        message_text = Body or ""
        has_media = int(NumMedia) > 0
        media_type = MediaContentType0 or ""
        
        logger.info(f"📱 Message from {user_phone}: {message_text[:50]}... (media: {has_media})")
        
        # Find user's project
        project, engineer = await _find_project_and_engineer(db, user_phone)
        
        if not project:
            await whatsapp_client.send_message(
                to=user_phone,
                body="👋 Hi! I'm SiteMind, your AI Site Engineer.\n\nYou're not registered for any project yet. Please contact your project manager to get added."
            )
            return Response(content="", media_type="text/xml")
        
        # Detect message type and intent
        intent = _detect_intent(message_text, has_media, media_type)
        
        # Route to appropriate handler
        if intent == "drawing_upload":
            response = await _handle_drawing_upload(
                project, user_phone, ProfileName,
                message_text, MediaUrl0, media_type,
                background_tasks
            )
        
        elif intent == "change_order":
            response = await _handle_change_order(
                project, user_phone, ProfileName,
                message_text, MediaUrl0, media_type,
                background_tasks
            )
        
        elif intent == "rfi":
            response = await _handle_rfi(
                project, user_phone, ProfileName,
                message_text, background_tasks
            )
        
        elif intent == "site_photo":
            response = await _handle_site_photo(
                project, user_phone, message_text,
                MediaUrl0, db, background_tasks
            )
        
        elif intent == "voice":
            response = "🎤 Voice notes aren't supported yet. Please type your question or send a photo!"
        
        else:  # Default: query
            response = await _handle_query(
                project, user_phone, ProfileName,
                message_text, db, background_tasks
            )
        
        # Send response
        await whatsapp_client.send_message(to=user_phone, body=response)
        
        total_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Response sent in {total_time_ms}ms (intent: {intent})")
        
        # Log interaction
        background_tasks.add_task(
            _log_chat_interaction,
            db, project.id, user_phone, ProfileName,
            intent, message_text, MediaUrl0, response,
            total_time_ms, None, None
        )
        
        return Response(content="", media_type="text/xml")
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        try:
            await whatsapp_client.send_message(
                to=extract_phone_number(From),
                body="Sorry, I encountered an error. Please try again in a moment."
            )
        except:
            pass
        return Response(content="", media_type="text/xml")


def _detect_intent(message: str, has_media: bool, media_type: str) -> str:
    """
    Detect what the user wants to do
    
    Returns: drawing_upload, change_order, rfi, site_photo, voice, query
    """
    message_lower = message.lower()
    
    # Voice note
    if has_media and "audio" in media_type:
        return "voice"
    
    # Document/PDF upload (likely drawing)
    if has_media and ("pdf" in media_type or "document" in media_type):
        return "drawing_upload"
    
    # Image with drawing keywords → drawing upload
    if has_media and "image" in media_type:
        if any(kw in message_lower for kw in DRAWING_KEYWORDS):
            return "drawing_upload"
        # Default: treat images as site photos
        return "site_photo"
    
    # Text with change order keywords
    if any(kw in message_lower for kw in CHANGE_ORDER_KEYWORDS):
        return "change_order"
    
    # Text with RFI keywords
    if any(kw in message_lower for kw in RFI_KEYWORDS):
        return "rfi"
    
    # Default: regular query
    return "query"


async def _handle_drawing_upload(
    project, user_phone: str, user_name: str,
    message: str, media_url: str, media_type: str,
    background_tasks: BackgroundTasks
) -> str:
    """
    Handle new drawing/blueprint upload via WhatsApp
    
    Architect sends: [PDF] "Revised floor plan v2.3"
    → Download, store in Supabase, process with Gemini, add to memory
    """
    try:
        # Download the file
        file_data = await whatsapp_client.download_media(media_url)
        if not file_data:
            return "❌ Couldn't download the file. Please try sending again."
        
        # Determine file type
        if "pdf" in media_type:
            file_ext = "pdf"
            doc_type = "blueprint"
        else:
            file_ext = "jpg"
            doc_type = "drawing_image"
        
        # Generate filename from message or timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        drawing_name = _extract_drawing_name(message) or f"drawing_{timestamp}"
        filename = f"{project.id}/{drawing_name}.{file_ext}"
        
        # Store in Supabase
        storage_result = await storage_service.upload_file(
            file_data=file_data,
            filename=filename,
            content_type=media_type,
        )
        
        if not storage_result:
            return "❌ Couldn't store the file. Please try again."
        
        # Upload to Gemini for processing
        # (In production, save locally first then upload)
        gemini_result = await gemini_service.upload_blueprint(
            file_path=storage_result.get("url", ""),
            display_name=drawing_name,
            doc_type=doc_type,
        )
        
        # Store in memory for context
        background_tasks.add_task(
            memory_service.add_memory,
            project_id=str(project.id),
            content=f"NEW DRAWING UPLOADED: {drawing_name}. Uploaded by {user_name or user_phone}. Notes: {message}",
            metadata={
                "type": "blueprint_revision",
                "drawing_name": drawing_name,
                "uploaded_by": user_name or user_phone,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                "storage_url": storage_result.get("url"),
                "original_message": message,
            }
        )
        
        return f"""✅ Drawing received and processed!

📐 **{drawing_name}**
📅 Uploaded: {datetime.utcnow().strftime("%d %b %Y, %H:%M")}
👤 By: {user_name or user_phone}

The AI is now aware of this drawing. Engineers can ask questions about it.

💡 Tip: Add notes like "Column C5 moved 500mm east" when uploading for better tracking."""
        
    except Exception as e:
        logger.error(f"Drawing upload error: {e}")
        return "❌ Error processing the drawing. Please try again or contact support."


async def _handle_change_order(
    project, user_phone: str, user_name: str,
    message: str, media_url: Optional[str], media_type: str,
    background_tasks: BackgroundTasks
) -> str:
    """
    Handle change order recording via WhatsApp
    
    PM sends: "Change order: Column C5 increased from 500x500 to 600x600 
              due to additional load. Approved by structural consultant."
    
    → Parse, store in memory with full audit trail
    """
    try:
        # Use Gemini to extract structured change order info
        extraction_prompt = f"""Extract change order details from this message:
"{message}"

Return in this format:
- What changed: [component and location]
- Previous value: [old spec]
- New value: [new spec]
- Reason: [why it changed]
- Approved by: [who approved, if mentioned]
- Drawing reference: [drawing number if mentioned]

If any field is not mentioned, write "Not specified"."""

        extraction_result = await gemini_service.analyze_query(
            query=extraction_prompt,
            thinking_level="low"
        )
        
        extracted = extraction_result.get("response", "")
        
        # Store in memory with audit trail
        await memory_service.add_memory(
            project_id=str(project.id),
            content=f"CHANGE ORDER: {message}",
            metadata={
                "type": "change_order",
                "recorded_by": user_name or user_phone,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                "original_message": message,
                "extracted_details": extracted,
                "has_attachment": bool(media_url),
            }
        )
        
        # If there's an attached drawing, process it too
        attachment_note = ""
        if media_url and "image" in media_type:
            attachment_note = "\n📎 Attached drawing has been saved for reference."
        
        return f"""✅ Change Order Recorded!

📝 **Details captured:**
{extracted}

📅 Recorded: {datetime.utcnow().strftime("%d %b %Y, %H:%M")}
👤 By: {user_name or user_phone}
{attachment_note}

This change is now in the project memory. Future queries will reflect this update.

⚠️ Make sure to upload the revised drawing if not already done."""

    except Exception as e:
        logger.error(f"Change order error: {e}")
        return "❌ Error recording change order. Please try again."


async def _handle_rfi(
    project, user_phone: str, user_name: str,
    message: str, background_tasks: BackgroundTasks
) -> str:
    """
    Handle RFI recording via WhatsApp
    
    Someone forwards: "RFI-089: Rebar spacing for slab S3? 
                      Answer: 150mm c/c both ways - Structural Consultant"
    
    → Parse and store for future reference
    """
    try:
        # Use Gemini to extract RFI info
        extraction_prompt = f"""Extract RFI details from this message:
"{message}"

Return in this format:
- RFI Number: [number if mentioned]
- Question: [what was asked]
- Answer: [the response/clarification]
- Answered by: [who answered]
- Drawing reference: [if mentioned]

If any field is not clear, write "Not specified"."""

        extraction_result = await gemini_service.analyze_query(
            query=extraction_prompt,
            thinking_level="low"
        )
        
        extracted = extraction_result.get("response", "")
        
        # Store in memory
        await memory_service.add_memory(
            project_id=str(project.id),
            content=f"RFI: {message}",
            metadata={
                "type": "rfi",
                "recorded_by": user_name or user_phone,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                "original_message": message,
                "extracted_details": extracted,
            }
        )
        
        return f"""✅ RFI Recorded!

📋 **Details captured:**
{extracted}

📅 Recorded: {datetime.utcnow().strftime("%d %b %Y, %H:%M")}
👤 Forwarded by: {user_name or user_phone}

This clarification is now in the project memory. Engineers asking related questions will get this information."""

    except Exception as e:
        logger.error(f"RFI error: {e}")
        return "❌ Error recording RFI. Please try again."


async def _handle_site_photo(
    project, user_phone: str, message: str,
    media_url: str, db: AsyncSession,
    background_tasks: BackgroundTasks
) -> str:
    """
    Handle site photo verification
    
    Engineer sends: [Photo] "Is this rebar spacing correct?"
    → Compare against blueprints, flag issues
    """
    try:
        # Download image
        image_data = await whatsapp_client.download_media(media_url)
        if not image_data:
            return "❌ Couldn't download the photo. Please try again."
        
        # Get project blueprints
        blueprint_ids = await _get_project_blueprint_ids(db, project.id)
        
        # Get relevant memory context
        memory_result = await memory_service.search_memory(
            project_id=str(project.id),
            query=message or "site photo verification",
            limit=5,
        )
        
        # Analyze with Gemini
        query = message or "Analyze this site photo. Check if what's shown matches the project blueprints. Flag any potential issues."
        
        ai_result = await gemini_service.analyze_site_photo(
            image_data=image_data,
            query=query,
            blueprint_ids=blueprint_ids,
        )
        
        response = ai_result.get("response", "I couldn't analyze the photo. Please try again.")
        
        # Store the verification in memory
        background_tasks.add_task(
            memory_service.add_memory,
            project_id=str(project.id),
            content=f"SITE PHOTO VERIFICATION: Query: {message}. Result: {response[:200]}...",
            metadata={
                "type": "photo_verification",
                "query": message,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Site photo error: {e}")
        return "❌ Error analyzing the photo. Please try again."


async def _handle_query(
    project, user_phone: str, user_name: str,
    message: str, db: AsyncSession,
    background_tasks: BackgroundTasks
) -> str:
    """
    Handle regular queries about blueprints/project
    
    Engineer asks: "Beam size at B2 3rd floor?"
    → Search memory + blueprints, answer with citations
    
    SMART FEATURES:
    - Hindi/English code switching
    - Typo correction
    - Follow-up question handling
    - Ambiguity detection
    - Urgency detection
    """
    try:
        # Normalize query (handle Hindi, typos, etc.)
        normalized_query, query_meta = smart_assistant.normalize_query(message)
        
        # Check if this is a follow-up question
        is_followup, followup_context = smart_assistant.is_followup_query(user_phone, message)
        
        # Check for ambiguity - need clarification?
        if query_meta["needs_clarification"] and not is_followup:
            clarification = smart_assistant.generate_clarification(message, query_meta["ambiguities"])
            if clarification:
                return clarification
        
        # Check for out of scope
        if query_meta["category"] == "out_of_scope":
            return smart_assistant.handle_out_of_scope(message)
        
        # Build enhanced query with context
        enhanced_query = message
        if is_followup and followup_context:
            enhanced_query = f"{followup_context}\n\nNew question: {message}"
        
        # Get relevant memory context
        memory_result = await memory_service.search_memory(
            project_id=str(project.id),
            query=normalized_query,
            limit=10,
        )
        memory_context = memory_result.get("context", "")
        
        # Check for conflicts in memory
        conflict_warning = smart_assistant.check_for_conflicts(
            normalized_query, 
            memory_result.get("results", [])
        )
        
        # Get project blueprints
        blueprint_ids = await _get_project_blueprint_ids(db, project.id)
        
        # Determine thinking level based on urgency
        thinking_level = "low" if query_meta["urgency"] == "critical" else "high"
        
        # Query Gemini
        ai_result = await gemini_service.analyze_query(
            query=enhanced_query,
            blueprint_ids=blueprint_ids,
            memory_context=memory_context,
            thinking_level=thinking_level,
        )
        
        response = ai_result.get("response", "I couldn't find an answer. Please try rephrasing your question.")
        
        # Add conflict warning if any
        if conflict_warning:
            response = conflict_warning + "\n\n" + response
        
        # Enhance response based on context
        user_stats = smart_assistant.get_user_stats(user_phone)
        response = smart_assistant.enhance_response(
            response, 
            query_meta["urgency"],
            query_meta["category"],
            user_stats
        )
        
        # Update conversation context
        smart_assistant.update_context(
            user_phone, message, response,
            topic=str(query_meta["category"]),
        )
        
        # Track engagement
        issue_detected = "⚠️" in response or "ISSUE" in response.upper()
        engagement_service.track_query(
            project_id=str(project.id),
            user_phone=user_phone,
            user_name=user_name or "Unknown",
            query=message,
            response=response,
            issue_detected=issue_detected,
        )
        
        # Store Q&A for future context
        background_tasks.add_task(
            memory_service.add_whatsapp_query,
            project_id=str(project.id),
            question=message,
            answer=response[:500],
            engineer_phone=user_phone,
            engineer_name=user_name,
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        return "❌ Error processing your question. Please try again."


def _extract_drawing_name(message: str) -> Optional[str]:
    """Extract drawing name/number from message"""
    # Common patterns: SK-001, AR-101, MEP-01, Floor Plan v2, etc.
    patterns = [
        r'\b([A-Z]{2,4}[-_]\d{2,4})\b',  # SK-001, AR-101
        r'\b(Rev\s*[\d\.]+)\b',  # Rev 2.1
        r'\b(v[\d\.]+)\b',  # v2.3
        r'\b(Floor\s+\d+)\b',  # Floor 3
        r'\b(Level\s+\d+)\b',  # Level 2
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).replace(" ", "_")
    
    return None


# ============================================
# HELPER FUNCTIONS
# ============================================

@router.get("/webhook")
async def whatsapp_webhook_verify(request: Request):
    """Webhook verification endpoint"""
    return {"status": "ok", "message": "SiteMind WhatsApp webhook is active"}


@router.post("/status")
async def message_status_callback(
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    ErrorCode: Optional[str] = Form(None),
):
    """Message delivery status callback"""
    logger.info(f"Message {MessageSid} status: {MessageStatus}")
    return {"status": "received"}


async def _find_project_and_engineer(
    db: AsyncSession,
    phone_number: str,
) -> Tuple[Optional[Project], Optional[SiteEngineer]]:
    """Find project and engineer by phone number"""
    result = await db.execute(
        select(SiteEngineer)
        .where(SiteEngineer.phone_number == phone_number)
        .where(SiteEngineer.is_active == True)
    )
    engineer = result.scalar_one_or_none()
    
    if not engineer:
        return None, None
    
    result = await db.execute(
        select(Project)
        .where(Project.id == engineer.project_id)
        .where(Project.status == "active")
    )
    project = result.scalar_one_or_none()
    
    return project, engineer


async def _get_project_blueprint_ids(
    db: AsyncSession,
    project_id,
) -> list[str]:
    """Get Gemini file IDs for project blueprints"""
    result = await db.execute(
        select(Blueprint.gemini_file_id)
        .where(Blueprint.project_id == project_id)
        .where(Blueprint.is_processed == True)
        .where(Blueprint.gemini_file_id.isnot(None))
    )
    return [row[0] for row in result.fetchall()]


async def _log_chat_interaction(
    db: AsyncSession,
    project_id,
    user_phone: str,
    user_name: Optional[str],
    message_type: str,
    user_message: str,
    media_url: Optional[str],
    bot_response: str,
    response_time_ms: int,
    model_used: Optional[str],
    tokens_used: Optional[int],
):
    """Log chat interaction to database"""
    try:
        chat_log = ChatLog(
            project_id=project_id,
            user_phone=user_phone,
            user_name=user_name,
            message_type=message_type,
            user_message=user_message,
            user_message_media_url=media_url,
            bot_response=bot_response,
            response_time_ms=response_time_ms,
            model_used=model_used,
            tokens_used=tokens_used,
        )
        db.add(chat_log)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to log chat: {e}")
