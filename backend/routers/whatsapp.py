"""
WhatsApp Webhook Router
Handles incoming messages from Twilio
"""

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
import httpx

from services import (
    gemini_service,
    memory_service,
    whatsapp_service,
    storage_service,
    billing_service,
    wow_service,
)
from database import db
from utils.logger import logger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages from Twilio
    """
    # Parse form data
    form = await request.form()
    data = dict(form)
    
    # Parse message
    message = whatsapp_service.parse_incoming(data)
    
    phone = message["from"]
    body = message["body"]
    num_media = message["num_media"]
    
    logger.info(f"📥 WhatsApp from {phone}: {body[:50]}...")
    
    try:
        # Get or create user
        user = await db.get_user_by_phone(phone)
        
        if not user:
            # Unknown user - send welcome
            await whatsapp_service.send_message(
                phone,
                "👋 Welcome! You're not registered with SiteMind yet.\n\nPlease contact your company admin to get access."
            )
            return PlainTextResponse("OK")
        
        # Get company and project info
        company = await db.get_company(user["company_id"])
        company_id = company["id"] if company else user["company_id"]
        company_name = company["name"] if company else "Company"
        
        # Update user activity
        await db.update_user_activity(user["id"])
        
        # Handle commands
        body_lower = body.lower().strip()
        
        if body_lower == "help":
            await whatsapp_service.send_help(phone)
            return PlainTextResponse("OK")
        
        if body_lower == "status":
            summary = billing_service.get_usage_summary(company_id)
            await whatsapp_service.send_message(phone, summary)
            return PlainTextResponse("OK")
        
        if body_lower in ["roi", "week1", "report"]:
            report = wow_service.format_week1_report(company_id, company_name)
            await whatsapp_service.send_message(phone, report)
            return PlainTextResponse("OK")
        
        # Handle media
        if num_media > 0:
            await handle_media(phone, message, company_id, user["id"])
            return PlainTextResponse("OK")
        
        # Regular query
        await handle_query(phone, body, company_id, user["id"], company_name)
        
        return PlainTextResponse("OK")
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        await whatsapp_service.send_alert(
            phone,
            "error",
            "Sorry, something went wrong. Please try again."
        )
        return PlainTextResponse("OK")


async def handle_query(
    phone: str,
    question: str,
    company_id: str,
    user_id: str,
    company_name: str,
):
    """Handle text query"""
    
    # Track for billing
    billing_service.track_query(company_id, company_name)
    
    # Get context from memory
    context = await memory_service.search(
        project_id=company_id,
        query=question,
        limit=5,
    )
    
    # Track memory recall (WOW moment!)
    if context:
        wow_service.track_memory_recall(user_id, company_id)
    
    # Query Gemini
    response = await gemini_service.query(
        question=question,
        context=context,
    )
    
    answer = response.get("answer", "Sorry, I couldn't process that.")
    
    # Check for code references (WOW moment!)
    has_code_ref = any(code in answer.lower() for code in ["is ", "is:", "nbc", "code"])
    wow_service.track_query(user_id, company_id, had_code_reference=has_code_ref)
    
    # Add memory context to response (shows AI remembers)
    if context:
        recalled = [c.get("content", str(c))[:80] for c in context[:2]]
        answer = wow_service.format_memory_response(answer, recalled)
    
    # Store Q&A in memory
    await memory_service.add_query(
        project_id=company_id,
        question=question,
        answer=answer,
        user_id=user_id,
    )
    
    # Log to database
    await db.log_query(
        company_id=company_id,
        project_id=None,
        user_id=user_id,
        question=question,
        answer=answer,
    )
    
    # Send response
    await whatsapp_service.send_answer(phone, question, answer)


async def handle_media(
    phone: str,
    message: dict,
    company_id: str,
    user_id: str,
):
    """Handle media messages (photos, documents)"""
    
    for i, (url, mime_type) in enumerate(zip(message["media_urls"], message["media_types"])):
        if not url:
            continue
        
        try:
            # Download media
            async with httpx.AsyncClient() as client:
                # Use Twilio credentials for media download
                auth = (
                    whatsapp_service.account_sid,
                    whatsapp_service.auth_token,
                )
                response = await client.get(url, auth=auth, timeout=60.0)
                
                if response.status_code != 200:
                    logger.error(f"Failed to download media: {response.status_code}")
                    continue
                
                content = response.content
            
            # Determine type
            is_image = mime_type and mime_type.startswith("image/")
            is_document = mime_type and (
                mime_type.startswith("application/pdf") or
                mime_type.startswith("application/")
            )
            
            if is_image:
                # Track for billing + WOW
                billing_service.track_photo(company_id)
                wow_service.track_photo(user_id, company_id)
                
                # Analyze image
                analysis = await gemini_service.analyze_image(
                    image_data=content,
                    mime_type=mime_type,
                    caption=message["body"],
                    analysis_type="general",
                )
                
                # Store photo
                upload = await storage_service.upload_photo(
                    file_content=content,
                    file_name=f"photo_{i}.jpg",
                    content_type=mime_type,
                    company_id=company_id,
                )
                
                # Log to database
                await db.log_photo(
                    company_id=company_id,
                    project_id=None,
                    user_id=user_id,
                    file_path=upload["path"],
                    file_size_bytes=len(content),
                    caption=message["body"],
                    analysis=analysis.get("analysis"),
                )
                
                # Send analysis
                await whatsapp_service.send_analysis(
                    phone,
                    "photo",
                    analysis.get("analysis", "Could not analyze image."),
                )
            
            elif is_document:
                # Track for billing
                billing_service.track_document(company_id)
                
                # Store document
                upload = await storage_service.upload_document(
                    file_content=content,
                    file_name=f"document_{i}.pdf",
                    content_type=mime_type,
                    company_id=company_id,
                )
                
                # Log to database
                await db.log_document(
                    company_id=company_id,
                    project_id=None,
                    user_id=user_id,
                    name=f"document_{i}",
                    file_path=upload["path"],
                    file_type=mime_type,
                    file_size_bytes=len(content),
                )
                
                await whatsapp_service.send_message(
                    phone,
                    f"📄 Document received and stored.\n\nFile: {upload['path']}\nSize: {len(content) / 1024:.1f} KB"
                )
            
            else:
                await whatsapp_service.send_message(
                    phone,
                    f"📎 Received file (type: {mime_type}). I can analyze images and PDFs."
                )
        
        except Exception as e:
            logger.error(f"Media handling error: {e}")
            await whatsapp_service.send_message(
                phone,
                f"❌ Error processing file: {str(e)}"
            )


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook for Twilio (if needed)"""
    return PlainTextResponse("OK")
