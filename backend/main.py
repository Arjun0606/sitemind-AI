"""
SiteMind API
AI-powered construction site management via WhatsApp

Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import whatsapp_router, admin_router, health_router
from utils.logger import logger


# ============================================================================
# APP
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered construction site management via WhatsApp",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(health_router)
app.include_router(whatsapp_router)
app.include_router(admin_router)


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    """Run on startup"""
    logger.info(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏗️  {settings.APP_NAME} v{settings.APP_VERSION}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Services:
  • Gemini:      {"✅" if settings.GOOGLE_API_KEY != "your_google_api_key" else "❌ Not configured"}
  • Supermemory: {"✅" if settings.SUPERMEMORY_API_KEY != "your_supermemory_api_key" else "❌ Not configured"}
  • Supabase:    {"✅" if settings.SUPABASE_URL != "your_supabase_url" else "❌ Not configured"}
  • Twilio:      {"✅" if settings.TWILIO_ACCOUNT_SID != "your_twilio_account_sid" else "❌ Not configured"}

Pricing:
  • Flat Fee:    ${settings.FLAT_FEE_USD}/month
  • Query:       ${settings.QUERY_PRICE_USD}/query
  • Document:    ${settings.DOCUMENT_PRICE_USD}/document
  • Photo:       ${settings.PHOTO_PRICE_USD}/photo
  • Storage:     ${settings.STORAGE_PRICE_USD}/GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
