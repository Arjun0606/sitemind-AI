"""
SiteMind WhatsApp Router - 100% AI-POWERED
===========================================

ZERO commands. ZERO pattern matching.
Just talk naturally - AI understands everything.

User just speaks naturally:
- "What is the column size at B2?"
- "Client approved marble flooring, extra 4L"
- "Spoke to architect, he said use 12mm rebar"
- "There's a leak in unit 1204"
- "Show me today's summary"
- "What RFIs are pending?"

AI understands intent and responds appropriately.
"""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime

from services import (
    whatsapp_service,
    memory_engine,
    awareness_engine,
    intelligence_engine,
    billing_service,
    project_manager,
    memory_service,
    gemini_service,
)
from database import db
from utils.logger import logger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


# =============================================================================
# MAIN WEBHOOK - 100% AI DRIVEN
# =============================================================================

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Main webhook handler - ALL messages go through AI
    
    NO commands. NO pattern matching.
    AI determines intent and takes appropriate action.
    """
    
    form = await request.form()
    data = dict(form)
    message = whatsapp_service.parse_incoming(data)
    
    phone = message["from"]
    body = message["body"].strip()
    num_media = message["num_media"]
    
    logger.info(f"📥 {phone}: {body[:50]}...")
    
    try:
        # Get user
        user = await db.get_user_by_phone(phone)
        
        if not user:
            await whatsapp_service.send_message(phone, get_welcome_message())
            return PlainTextResponse("OK")
        
        # Context
        company_id = user.get("company_id", "default")
        user_id = user.get("id", phone)
        user_name = user.get("name", "User")
        
        current_project = project_manager.get_current_project(user_id, company_id)
        project_id = current_project.id if current_project else "default"
        project_name = current_project.name if current_project else "Project"
        
        await db.update_user_activity(user_id)
        
        # =====================================================
        # MEDIA HANDLING - AI processes everything
        # =====================================================
        
        if num_media > 0:
            response = await process_media_with_ai(
                phone, message, user_id, user_name, company_id, project_id
            )
            await whatsapp_service.send_message(phone, response)
            return PlainTextResponse("OK")
        
        # =====================================================
        # TEXT MESSAGE - 100% AI PROCESSING
        # =====================================================
        
        response = await process_message_with_ai(
            body, user_name, user_id, company_id, project_id, project_name
        )
        
        billing_service.track_query(company_id)
        
        await whatsapp_service.send_message(phone, response)
        return PlainTextResponse("OK")
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        await whatsapp_service.send_message(phone, "Something went wrong. Please try again.")
        return PlainTextResponse("OK")


# =============================================================================
# AI PROCESSING - THE HEART OF SITEMIND
# =============================================================================

async def process_message_with_ai(
    message: str,
    user_name: str,
    user_id: str,
    company_id: str,
    project_id: str,
    project_name: str,
) -> str:
    """
    Process ANY message with AI - no pattern matching
    
    AI determines:
    1. What is the user's INTENT?
    2. What ACTION should be taken?
    3. What RESPONSE should be given?
    """
    
    # Get project context from memory
    context = await memory_service.get_context(
        company_id=company_id,
        project_id=project_id,
        query=message,
        user_id=user_id,
    )
    
    # AI determines intent and generates response
    prompt = f"""You are SiteMind, an AI assistant for construction project management.

PROJECT: {project_name}
USER: {user_name}
MESSAGE: {message}

RELEVANT PROJECT CONTEXT:
{context if context else "No previous context stored yet."}

YOUR JOB:
1. Understand what the user wants
2. Take the appropriate action
3. Give a helpful, natural response

INTENT CATEGORIES (detect automatically):
- QUESTION: User is asking for information → Search memory and answer with citations
- DECISION: User is communicating a decision/approval → Log it and confirm
- PHONE_CALL: User is logging a phone conversation → Log it with details
- RFI: User is asking for clarification that needs expert response → Create RFI
- ISSUE: User is reporting a problem → Log the issue
- PROGRESS: User is sharing work completion update → Record progress
- SUMMARY_REQUEST: User wants a summary → Generate summary
- RFI_STATUS: User wants to know pending RFIs → List them
- ISSUE_STATUS: User wants to know open issues → List them
- RISK_STATUS: User wants to know risks → Show risks
- REPORT_REQUEST: User wants a report → Generate report
- GENERAL: General conversation or update → Store and acknowledge

IMPORTANT RULES:
1. ALWAYS be helpful and conversational
2. For QUESTIONS: Answer with specific citations (drawing name, date, who said it)
3. For DECISIONS: Confirm the decision was logged with full details
4. For ISSUES: Acknowledge and note severity
5. For SUMMARIES/REPORTS: Generate comprehensive summaries
6. Never ask user to use commands or specific formats
7. Respond in the same language the user used (English/Hindi/Hinglish)

NOW RESPOND TO THE USER:"""

    # Call AI
    ai_response = await gemini_service.query(prompt)
    
    # Also process in background for storage and detection
    await process_for_storage(message, user_name, user_id, company_id, project_id, ai_response)
    
    return ai_response


async def process_for_storage(
    message: str,
    user_name: str,
    user_id: str,
    company_id: str,
    project_id: str,
    ai_response: str,
):
    """
    Background processing - AI determines what to store
    """
    
    # Have AI classify and extract
    classification_prompt = f"""Analyze this message and extract structured information.

MESSAGE: {message}
FROM: {user_name}

Return JSON with:
{{
    "intent": "question|decision|phone_call|rfi|issue|progress|summary_request|general",
    "should_store": true/false,
    "decision_content": "if decision, what was decided",
    "issue_content": "if issue, what is the problem",
    "issue_severity": "high|medium|low",
    "issue_location": "location if mentioned",
    "progress_work": "if progress, what work",
    "progress_location": "where",
    "progress_status": "status",
    "financial_amount": "if any amount mentioned in rupees",
    "people_mentioned": ["names mentioned"],
    "key_information": "most important info to remember"
}}

Only return valid JSON, nothing else."""

    try:
        classification = await gemini_service.query(classification_prompt)
        data = gemini_service.extract_json(classification)
        
        if not data:
            # If JSON extraction failed, just store as general message
            data = {"intent": "general", "should_store": True}
        
        intent = data.get("intent", "general")
        
        # Store based on intent
        if intent == "decision" and data.get("decision_content"):
            await memory_engine.log_decision(
                data["decision_content"],
                user_name,
                company_id,
                project_id,
            )
        
        elif intent == "issue" and data.get("issue_content"):
            await awareness_engine.detect_issue(
                message, user_name, company_id, project_id
            )
        
        elif intent == "progress" and data.get("progress_work"):
            await awareness_engine.detect_progress(
                message, user_name, company_id, project_id
            )
        
        elif intent == "rfi":
            await memory_engine.create_rfi(
                title=message[:50],
                question=message,
                raised_by=user_name,
                company_id=company_id,
                project_id=project_id,
            )
        
        elif intent == "phone_call":
            await memory_engine.log_decision(
                f"📞 Phone call: {message}",
                user_name,
                company_id,
                project_id,
            )
        
        # Always store the message in memory (except summary requests)
        if data.get("should_store", True) and intent not in ["summary_request", "rfi_status", "issue_status", "risk_status", "report_request"]:
            await memory_service.add_memory(
                company_id=company_id,
                project_id=project_id,
                content=f"{user_name}: {message}",
                memory_type=intent,
                metadata={
                    "user": user_name,
                    "financial_amount": data.get("financial_amount"),
                    "people_mentioned": data.get("people_mentioned"),
                    "key_information": data.get("key_information"),
                },
                user_id=user_id,
            )
        
        # Detect approvers
        await awareness_engine.detect_approver(message, user_name, company_id, project_id)
        
    except Exception as e:
        logger.error(f"Storage processing error: {e}")


async def process_media_with_ai(
    phone: str,
    message: dict,
    user_id: str,
    user_name: str,
    company_id: str,
    project_id: str,
) -> str:
    """
    Process media uploads with AI understanding
    """
    from services.storage_service import storage_service
    import httpx
    
    caption = message.get("body", "").strip()
    responses = []
    
    for url, mime_type in zip(message.get("media_urls", []), message.get("media_types", [])):
        if not url:
            continue
        
        try:
            async with httpx.AsyncClient() as client:
                auth = (whatsapp_service.account_sid, whatsapp_service.auth_token)
                response = await client.get(url, auth=auth, timeout=60.0)
                
                if response.status_code != 200:
                    continue
                
                content = response.content
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_name = caption or f"file_{timestamp}"
            
            # PDF/Document
            if "pdf" in mime_type or "document" in mime_type:
                # Store
                await storage_service.upload_document(
                    file_content=content,
                    file_name=f"{file_name}.pdf",
                    content_type=mime_type,
                    company_id=company_id,
                    project_id=project_id,
                )
                
                # Extract with AI
                drawing = await memory_engine.extract_drawing_info(
                    document_text=f"Drawing: {file_name}",
                    file_name=file_name,
                    company_id=company_id,
                    project_id=project_id,
                    uploaded_by=user_name,
                )
                
                billing_service.track_document(company_id)
                
                responses.append(f"""📄 *{file_name}* stored!

Uploaded by: {user_name}
Date: {datetime.utcnow().strftime('%d-%b-%Y %H:%M')}

I'll remember this file. Ask me "send latest {file_name.split('.')[0]}" anytime to get it back.""")
            
            # Image
            elif mime_type.startswith("image/"):
                await storage_service.upload_photo(
                    file_content=content,
                    file_name=f"{file_name}.jpg",
                    content_type=mime_type,
                    company_id=company_id,
                    project_id=project_id,
                )
                
                # Store in memory with caption context
                await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=f"Photo uploaded by {user_name}: {caption or 'Site photo'}",
                    memory_type="photo",
                    metadata={"caption": caption, "uploaded_by": user_name},
                    user_id=user_id,
                )
                
                billing_service.track_photo(company_id)
                
                responses.append(f"📷 Photo saved.{f' Caption: {caption}' if caption else ''}")
            
            else:
                responses.append("📎 File received and stored.")
                
        except Exception as e:
            logger.error(f"Media error: {e}")
            responses.append("Couldn't process one of the files.")
    
    return "\n\n".join(responses) if responses else "Received your files."


# =============================================================================
# MESSAGES
# =============================================================================

def get_welcome_message() -> str:
    return """👋 *Welcome to SiteMind*

I'm your project's memory. I help you:

• Remember every decision and approval
• Track issues and RFIs
• Store and manage drawings
• Generate summaries

*To get started*, ask your admin to add you to a project.

Once added, just chat normally - I understand and remember everything.

Try:
• "Who approved the tile change?"
• "What was decided about balcony?"
• "Show me today's summary"
• "What RFIs are pending?"

_Everything you share becomes searchable forever._"""


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/webhook")
async def verify():
    return PlainTextResponse("SiteMind Active")


@router.get("/health")
async def health():
    return {"status": "ok"}
