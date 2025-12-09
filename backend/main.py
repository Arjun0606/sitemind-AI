"""
SiteMind API - FINAL CLEAN VERSION
===================================

AI-powered construction project memory via WhatsApp.

WHAT WE DO:
- Remember everything said (decisions, approvals, issues)
- Store and track drawing versions
- AI-powered intent detection
- Search project history
- Generate summaries and reports
- Track RFIs and issues

Run: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import whatsapp_router, admin_router, health_router, dashboard_router
from utils.logger import logger


# =============================================================================
# APP
# =============================================================================

app = FastAPI(
    title="SiteMind API",
    version="1.0.0",
    description="Your Project's Memory - Never lose a decision, drawing, or discussion",
)

# CORS - Configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROUTERS
# =============================================================================

app.include_router(health_router)
app.include_router(whatsapp_router)
app.include_router(dashboard_router)
app.include_router(admin_router)


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup():
    """Run on startup"""
    
    # Check service configuration
    gemini_ok = settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "your_google_api_key"
    supermemory_ok = settings.SUPERMEMORY_API_KEY and settings.SUPERMEMORY_API_KEY != "your_supermemory_api_key"
    supabase_ok = settings.SUPABASE_URL and settings.SUPABASE_URL != "your_supabase_url"
    twilio_ok = settings.TWILIO_ACCOUNT_SID and settings.TWILIO_ACCOUNT_SID != "your_twilio_account_sid"
    
    logger.info(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 SITEMIND - YOUR PROJECT'S MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Never lose a decision, drawing, or discussion.

CAPABILITIES:
✅ Remember everything typed
✅ Store & track drawing versions
✅ AI intent detection (decisions, issues, RFIs)
✅ Search project history
✅ Generate summaries
✅ Track RFIs and issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SERVICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Gemini (AI):       {"✅ Connected" if gemini_ok else "❌ Not configured"}
  Supermemory:       {"✅ Connected" if supermemory_ok else "❌ Not configured"}
  Supabase:          {"✅ Connected" if supabase_ok else "❌ Not configured"}
  Twilio:            {"✅ Connected" if twilio_ok else "❌ Not configured"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  WhatsApp:          POST /whatsapp/webhook
  Dashboard API:     GET  /api/dashboard/*
  Health:            GET  /health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 SiteMind ready!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# =============================================================================
# ROOT
# =============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "SiteMind API",
        "version": "1.0.0",
        "description": "Connected Intelligence for Construction",
        "docs": "/docs",
        "health": "/health",
    }


# =============================================================================
# SCHEDULED TASKS (Call via cron or scheduler)
# =============================================================================

@app.post("/internal/run-reminders/{company_id}")
async def trigger_reminders(company_id: str):
    """
    Trigger reminder checks for a company
    Call this via cron job: 0 9 * * * curl -X POST http://localhost:8000/internal/run-reminders/company-id
    """
    from services.reminder_service import reminder_service
    
    result = await reminder_service.check_and_send_reminders(company_id)
    return {"status": "ok", "reminders_sent": result}


@app.post("/internal/morning-summary/{company_id}")
async def trigger_morning_summary(company_id: str):
    """
    Trigger morning summary for a company
    Call this via cron job: 0 8 * * * curl -X POST http://localhost:8000/internal/morning-summary/company-id
    """
    from services.reminder_service import reminder_service
    
    count = await reminder_service.send_morning_summary(company_id)
    return {"status": "ok", "projects_processed": count}


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
