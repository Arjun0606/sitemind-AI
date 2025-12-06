"""
SiteMind WhatsApp Webhook Router
Handles incoming WhatsApp messages from Twilio
"""

import time
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Request, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from config import settings
from utils.logger import logger
from utils.helpers import extract_phone_number, calculate_cost
from utils.database import get_async_session
from models.database import Project, SiteEngineer, Blueprint, ChatLog
from services.gemini_service import gemini_service
from services.memory_service import memory_service
from services.whatsapp_client import whatsapp_client


router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


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
    Main WhatsApp webhook endpoint
    Receives messages from Twilio and processes them
    """
    start_time = time.time()
    
    try:
        # Extract phone number
        user_phone = extract_phone_number(From)
        logger.info(f"Incoming message from {user_phone}: {Body[:100] if Body else '[media]'}...")
        
        # Find the project and site engineer
        project, engineer = await _find_project_and_engineer(db, user_phone)
        
        if not project:
            # Unknown user - send helpful message
            await whatsapp_client.send_message(
                to=user_phone,
                body="👋 Hi! I'm SiteMind, your AI Site Engineer.\n\nIt looks like you're not registered for any project yet. Please contact your project manager to get added to SiteMind."
            )
            return Response(content="", media_type="text/xml")
        
        # Determine message type and extract content
        message_type = "text"
        user_message = Body or ""
        
        # Handle images (site photos)
        if int(NumMedia) > 0 and MediaContentType0 and "image" in MediaContentType0:
            message_type = "image"
            if not Body:
                user_message = "What can you tell me about this image?"
        
        # Handle voice notes - not supported, ask for text
        elif int(NumMedia) > 0 and MediaContentType0 and "audio" in MediaContentType0:
            await whatsapp_client.send_message(
                to=user_phone,
                body="🎤 Voice notes are not supported yet. Please type your question instead!"
            )
            return Response(content="", media_type="text/xml")
        
        # Check if message is empty
        if not user_message.strip():
            await whatsapp_client.send_message(
                to=user_phone,
                body="I received an empty message. Please ask your question about the blueprints."
            )
            return Response(content="", media_type="text/xml")
        
        # Get project memory context
        memory_result = await memory_service.search_memory(
            project_id=str(project.id),
            query=user_message,
            limit=5,
        )
        memory_context = memory_result.get("context", "")
        
        # Get project blueprints (Gemini file IDs)
        blueprint_ids = await _get_project_blueprint_ids(db, project.id)
        
        # Process query with Gemini
        if message_type == "image" and MediaUrl0:
            # Download image and analyze with blueprint context
            image_data = await whatsapp_client.download_media(MediaUrl0)
            if image_data:
                ai_result = await gemini_service.analyze_site_photo(
                    image_data=image_data,
                    query=user_message,
                    blueprint_ids=blueprint_ids,
                )
            else:
                ai_result = await gemini_service.analyze_query(
                    query=user_message,
                    blueprint_ids=blueprint_ids,
                    memory_context=memory_context,
                )
        else:
            ai_result = await gemini_service.analyze_query(
                query=user_message,
                blueprint_ids=blueprint_ids,
                memory_context=memory_context,
            )
        
        # Get the response
        response_text = ai_result.get("response", "I couldn't process your query. Please try again.")
        
        # Send response via WhatsApp
        send_result = await whatsapp_client.send_message(
            to=user_phone,
            body=response_text,
        )
        
        # Calculate total response time
        total_time_ms = int((time.time() - start_time) * 1000)
        
        # Log the chat interaction (in background)
        background_tasks.add_task(
            _log_chat_interaction,
            db=db,
            project_id=project.id,
            user_phone=user_phone,
            user_name=ProfileName,
            message_type=message_type,
            user_message=Body or "",
            media_url=MediaUrl0,
            bot_response=response_text,
            response_time_ms=total_time_ms,
            model_used=ai_result.get("model_used"),
            tokens_used=ai_result.get("tokens_used"),
        )
        
        logger.info(f"Response sent to {user_phone} in {total_time_ms}ms")
        
        # Return empty TwiML response (we're sending via API)
        return Response(content="", media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        
        # Try to send error message
        try:
            await whatsapp_client.send_message(
                to=extract_phone_number(From),
                body="Sorry, I encountered an error processing your message. Please try again in a moment."
            )
        except:
            pass
        
        return Response(content="", media_type="text/xml")


@router.get("/webhook")
async def whatsapp_webhook_verify(request: Request):
    """
    Webhook verification endpoint (for Meta Cloud API if needed)
    """
    # For Twilio, this isn't strictly necessary, but useful for testing
    return {"status": "ok", "message": "SiteMind WhatsApp webhook is active"}


@router.post("/status")
async def message_status_callback(
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    ErrorCode: Optional[str] = Form(None),
):
    """
    Callback for message delivery status updates
    """
    logger.info(f"Message {MessageSid} status: {MessageStatus} (error: {ErrorCode})")
    return {"status": "received"}


async def _find_project_and_engineer(
    db: AsyncSession,
    phone_number: str,
) -> tuple[Optional[Project], Optional[SiteEngineer]]:
    """
    Find project and site engineer by phone number
    """
    # First, find the site engineer
    result = await db.execute(
        select(SiteEngineer)
        .where(SiteEngineer.phone_number == phone_number)
        .where(SiteEngineer.is_active == True)
    )
    engineer = result.scalar_one_or_none()
    
    if not engineer:
        return None, None
    
    # Get the associated project
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
    """
    Get Gemini file IDs for all processed blueprints in a project
    """
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
    """
    Log chat interaction to database (runs in background)
    """
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
        logger.error(f"Failed to log chat interaction: {e}")

