"""
SiteMind WhatsApp Webhook Router
The heart of the product - handles all user interactions

Every message is an opportunity to deliver value.
"""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime
import httpx
import re

from services import (
    gemini_service,
    memory_service,
    whatsapp_service,
    storage_service,
    billing_service,
    wow_service,
    intelligence_service,
    daily_brief_service,
    report_service,
    project_manager,
    command_handler,
    alert_service,
    leakage_prevention_service,
    office_sync_service,
    sitemind_core,
    document_ingestion_service,
)
from database import db
from utils.logger import logger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages from Twilio
    
    This is where the magic happens.
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
                "👋 Welcome! You're not registered with SiteMind yet.\n\nPlease contact your company admin to get access, or visit sitemind.ai to sign up."
            )
            return PlainTextResponse("OK")
        
        # Get company info
        company = await db.get_company(user["company_id"])
        company_id = company["id"] if company else user["company_id"]
        company_name = company["name"] if company else "Company"
        user_id = user.get("id", phone)
        
        # Update user activity
        await db.update_user_activity(user_id)
        
        # Get current project
        current_project = project_manager.get_current_project(user_id, company_id)
        project_id = current_project.id if current_project else None
        project_name = current_project.name if current_project else "Default"
        
        # Track daily activity
        daily_brief_service.track_user(project_id or company_id, user_id)
        
        # =====================================================================
        # HANDLE COMMANDS
        # =====================================================================
        
        cmd, args = command_handler.parse(body)
        
        if cmd:
            response = await handle_command(
                cmd, args, phone, user_id, company_id, company_name, 
                project_id, project_name, current_project
            )
            if response:
                await whatsapp_service.send_message(phone, response)
                return PlainTextResponse("OK")
        
        # =====================================================================
        # HANDLE MEDIA
        # =====================================================================
        
        if num_media > 0:
            await handle_media(phone, message, company_id, user_id, project_id)
            return PlainTextResponse("OK")
        
        # =====================================================================
        # HANDLE QUERY
        # =====================================================================
        
        await handle_query(
            phone, body, company_id, user_id, company_name,
            project_id, project_name
        )
        
        return PlainTextResponse("OK")
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        await whatsapp_service.send_alert(
            phone,
            "error",
            "Sorry, something went wrong. Please try again."
        )
        return PlainTextResponse("OK")


# =============================================================================
# COMMAND HANDLER
# =============================================================================

async def handle_command(
    cmd: str,
    args: dict,
    phone: str,
    user_id: str,
    company_id: str,
    company_name: str,
    project_id: str,
    project_name: str,
    current_project,
) -> str:
    """Handle command and return response"""
    
    # Help
    if cmd in ["help", "_cmd_hello"]:
        return command_handler._cmd_help()
    
    # Projects list
    if cmd in ["projects", "_cmd_projects"]:
        return project_manager.format_project_list(company_id)
    
    # Current project
    if cmd in ["project", "_cmd_current_project"]:
        if current_project:
            return project_manager.format_current_project(current_project)
        return "No project selected. Type 'projects' to see your projects."
    
    # Switch project
    if cmd == "_cmd_switch":
        match = args.get("match")
        if match:
            project_name_to_switch = match.group(1)
            project = project_manager.switch_project(user_id, company_id, project_name_to_switch)
            if project:
                return project_manager.format_switch_success(project)
            return f"❌ Project '{project_name_to_switch}' not found. Type 'projects' to see available projects."
    
    # Status
    if cmd in ["status", "_cmd_status"]:
        return billing_service.get_usage_summary(company_id)
    
    # ROI
    if cmd in ["roi", "_cmd_roi"]:
        return wow_service.format_week1_report(company_id, company_name)
    
    # Report
    if cmd in ["report", "week", "_cmd_report"]:
        usage = billing_service.get_usage(company_id) or {}
        roi = wow_service.get_week1_roi(company_id)
        
        report = report_service.generate_weekly_report(
            company_id=company_id,
            company_name=company_name,
            activity_data={
                "queries": usage.get("queries", 0),
                "photos": usage.get("photos", 0),
                "documents": usage.get("documents", 0),
                "safety_flags": roi.get("safety_flags", 0),
                "conflicts": 0,
                "active_users": roi.get("active_users", 0),
                "active_projects": len(project_manager.get_active_projects(company_id)),
            },
        )
        return report_service.format_weekly_whatsapp(report)
    
    # Brief
    if cmd in ["brief", "_cmd_brief"]:
        brief = daily_brief_service.generate_brief(
            project_id or company_id,
            project_name or company_name,
        )
        return daily_brief_service.format_brief_whatsapp(brief)
    
    # Team
    if cmd in ["team", "_cmd_team"]:
        users = await db.get_company_users(company_id)
        if not users:
            return "No team members found."
        
        msg = f"👥 *{company_name} Team*\n\n"
        for u in users:
            role_icon = {"admin": "👑", "pm": "📊", "site_engineer": "🔧"}.get(u.get("role", ""), "👤")
            msg += f"{role_icon} {u.get('name', 'Unknown')} - {u.get('phone', '')}\n"
        
        msg += "\n_To add: 'add +91xxx Name'_"
        return msg
    
    # Search
    if cmd == "_cmd_search":
        match = args.get("match")
        if match:
            query = match.group(1)
            results = await memory_service.search(
                company_id=company_id,
                query=query,
                project_id=project_id,
                limit=5,
            )
            
            if not results:
                return f"🔍 No results found for '{query}'"
            
            msg = f"🔍 *Search Results for '{query}'*\n\n"
            for i, r in enumerate(results, 1):
                content = r.get("content", str(r))[:100]
                msg += f"{i}. {content}...\n\n"
            
            return msg
    
    return None  # Not a handled command


# =============================================================================
# QUERY HANDLER
# =============================================================================

async def handle_query(
    phone: str,
    question: str,
    company_id: str,
    user_id: str,
    company_name: str,
    project_id: str,
    project_name: str,
):
    """
    Handle text query - THE CORE AI EXPERIENCE
    
    Uses sitemind_core which:
    1. Stores the message (info dump)
    2. Retrieves ALL relevant context
    3. Generates response with CITATIONS
    4. Stores the conversation
    """
    
    # Track for billing
    billing_service.track_query(company_id, company_name)
    daily_brief_service.track_query(project_id or company_id)
    
    # Get user info
    user = await db.get_user_by_phone(phone)
    user_name = user.get("name", "") if user else ""
    
    # USE SITEMIND CORE - This is the magic!
    # It handles: context retrieval, AI response, citations, storage
    result = await sitemind_core.process_message(
        message=question,
        company_id=company_id,
        project_id=project_id or "default",
        user_id=user_id,
        user_name=user_name,
    )
    
    answer = result.get("answer", "Sorry, I couldn't process that.")
    context_used = result.get("context_used", 0)
    
    # Track memory recall (WOW moment!)
    if context_used > 0:
        wow_service.track_memory_recall(user_id, company_id)
    
    # Track for office sync
    office_sync_service.track_query(
        project_id=project_id or "default",
        company_id=company_id,
        question=question,
        user_id=user_id,
    )
    
    # Track code references
    has_code_ref = any(code in answer.lower() for code in ["is ", "is:", "nbc", "code", "clause"])
    wow_service.track_query(user_id, company_id, had_code_reference=has_code_ref)
    
    # Add project indicator
    if project_name and project_name != "Default":
        answer += f"\n\n🏗️ _{project_name}_"
    
    # Log to database (sitemind_core already stores in Supermemory)
    await db.log_query(
        company_id=company_id,
        project_id=project_id,
        user_id=user_id,
        question=question,
        answer=answer,
    )
    
    # Send response
    await whatsapp_service.send_answer(phone, question, answer)


# =============================================================================
# MEDIA HANDLER
# =============================================================================

async def handle_media(
    phone: str,
    message: dict,
    company_id: str,
    user_id: str,
    project_id: str,
):
    """Handle media messages (photos, documents)"""
    
    for i, (url, mime_type) in enumerate(zip(message["media_urls"], message["media_types"])):
        if not url:
            continue
        
        try:
            # Download media
            async with httpx.AsyncClient() as client:
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
                "document" in mime_type.lower()
            )
            
            if is_image:
                await handle_image(
                    phone, content, mime_type, message["body"],
                    company_id, user_id, project_id, i
                )
            
            elif is_document:
                await handle_document(
                    phone, content, mime_type,
                    company_id, user_id, project_id, i
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


async def handle_image(
    phone: str,
    content: bytes,
    mime_type: str,
    caption: str,
    company_id: str,
    user_id: str,
    project_id: str,
    index: int,
):
    """
    Handle image - site photos, drawings, etc.
    
    DUMP EVERYTHING approach:
    1. User sends any image via WhatsApp
    2. If it's a drawing → ingest it
    3. If it's a photo → analyze with context
    4. Store everything in memory
    """
    
    # Track for billing + WOW
    billing_service.track_photo(company_id)
    wow_service.track_photo(user_id, company_id)
    daily_brief_service.track_photo(project_id or company_id)
    
    # Get user info
    user = await db.get_user_by_phone(phone)
    user_name = user.get("name", "") if user else ""
    
    # Check if this looks like a drawing (based on caption)
    is_drawing = False
    if caption:
        caption_lower = caption.lower()
        if any(word in caption_lower for word in ['drawing', 'plan', 'layout', 'detail', 'section', 'elevation']):
            is_drawing = True
    
    if is_drawing:
        # Treat as drawing - ingest it
        filename = f"drawing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        
        await whatsapp_service.send_message(phone, "📐 Processing drawing...")
        
        doc = await document_ingestion_service.ingest_document(
            company_id=company_id,
            project_id=project_id or "default",
            filename=filename,
            file_data=content,
            doc_type=document_ingestion_service.DocumentType.DRAWING,
            uploaded_by=user_name or user_id,
        )
        
        analysis_text = f"""*Drawing Analyzed & Stored*

📐 {doc.filename}
🔍 {len(doc.memory_ids)} searchable chunks

{doc.summary[:300] if doc.summary else 'Drawing processed'}

_Ask me anything about this drawing!_"""
    
    else:
        # Regular photo - use sitemind_core for analysis with context
        result = await sitemind_core.process_message(
            message=caption or "Analyze this site photo",
            company_id=company_id,
            project_id=project_id or "default",
            user_id=user_id,
            user_name=user_name,
            photo_data=content,
        )
        
        analysis_text = result.get("answer", "Could not analyze image.")
    
    # Safety check on analysis
    safety = await intelligence_service.analyze_safety(
        image_analysis=analysis_text,
        project_id=project_id,
    )
    
    if not safety["is_safe"]:
        analysis_text += "\n\n⚠️ *Safety Concerns Detected:*"
        for issue in safety["issues"][:3]:
            analysis_text += f"\n• {issue}"
        
        wow_service.track_safety_flag(user_id, company_id)
        daily_brief_service.track_safety_flag(project_id or company_id)
    
    # Store photo
    upload = await storage_service.upload_photo(
        file_content=content,
        file_name=f"photo_{index}.jpg",
        content_type=mime_type,
        company_id=company_id,
        project_id=project_id,
    )
    
    # Store in memory
    await memory_service.add_photo_analysis(
        company_id=company_id,
        project_id=project_id or "default",
        caption=caption or "",
        analysis=analysis_text,
        file_path=upload.get("path"),
        photo_type=analysis_type,
        user_id=user_id,
    )
    
    # Log to database
    await db.log_photo(
        company_id=company_id,
        project_id=project_id,
        user_id=user_id,
        file_path=upload.get("path", ""),
        file_size_bytes=len(content),
        caption=caption,
        analysis=analysis_text,
    )
    
    # Send analysis
    await whatsapp_service.send_analysis(phone, "photo", analysis_text)


async def handle_document(
    phone: str,
    content: bytes,
    mime_type: str,
    company_id: str,
    user_id: str,
    project_id: str,
    index: int,
):
    """
    Handle document upload - PDF, drawings, specs, etc.
    
    DUMP EVERYTHING approach:
    1. User sends any document via WhatsApp
    2. We process it with Gemini
    3. Store in Supermemory
    4. Now AI can answer questions about it!
    """
    
    # Track for billing
    billing_service.track_document(company_id)
    daily_brief_service.track_document(project_id or company_id)
    
    # Get user info for citation
    user = await db.get_user_by_phone(phone)
    user_name = user.get("name", "") if user else ""
    
    # Determine filename from mime type
    ext = "pdf"
    if "image" in mime_type:
        ext = "png"
    filename = f"upload_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{index}.{ext}"
    
    # Send processing message
    await whatsapp_service.send_message(
        phone,
        f"📄 Processing document... ({len(content) / 1024:.1f} KB)"
    )
    
    try:
        # INGEST THE DOCUMENT - This is the magic!
        doc = await document_ingestion_service.ingest_document(
            company_id=company_id,
            project_id=project_id or "default",
            filename=filename,
            file_data=content,
            uploaded_by=user_name or user_id,
        )
        
        # Store in Supabase too
        upload = await storage_service.upload_document(
            file_content=content,
            file_name=filename,
            content_type=mime_type,
            company_id=company_id,
            project_id=project_id,
        )
        
        # Log to database
        await db.log_document(
            company_id=company_id,
            project_id=project_id,
            user_id=user_id,
            name=filename,
            file_path=upload.get("path", ""),
            file_type=mime_type,
            file_size_bytes=len(content),
        )
        
        # Build response with what we found
        summary = doc.summary[:200] if doc.summary else "Document processed"
        key_count = len(doc.key_info)
        chunks = len(doc.memory_ids)
        
        await whatsapp_service.send_message(
            phone,
            f"""✅ *Document Ingested!*

📄 {filename}
📊 {chunks} searchable chunks created
🔍 {key_count} key items extracted

*Summary:*
{summary}...

━━━━━━━━━━━━━━━━━━━━━━

_Now ask me anything about this document!_
_Example: "What does the drawing say about column sizes?"_"""
        )
        
    except Exception as e:
        logger.error(f"Document ingestion error: {e}")
        await whatsapp_service.send_message(
            phone,
            f"❌ Error processing document: {str(e)}\n\nThe file was saved but couldn't be analyzed."
        )


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook for Twilio"""
    return PlainTextResponse("OK")
