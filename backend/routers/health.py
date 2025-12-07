"""
Health Check Router
"""

from fastapi import APIRouter
from config import settings

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@router.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "services": {
            "gemini": "configured" if settings.GOOGLE_API_KEY != "your_google_api_key" else "not_configured",
            "supermemory": "configured" if settings.SUPERMEMORY_API_KEY != "your_supermemory_api_key" else "not_configured",
            "supabase": "configured" if settings.SUPABASE_URL != "your_supabase_url" else "not_configured",
            "twilio": "configured" if settings.TWILIO_ACCOUNT_SID != "your_twilio_account_sid" else "not_configured",
        },
    }

