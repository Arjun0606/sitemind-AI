"""
SiteMind API
The AI Layer for Construction

Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from utils.logger import logger

# Import routers
from routers.whatsapp import router as whatsapp_router
from routers.admin import router as admin_router

# Import services for health check
from services import (
    GeminiService,
    MemoryService,
    WhatsAppClient,
    StorageService,
)


# =============================================================================
# LIFESPAN (Startup/Shutdown)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("🚀 SiteMind API starting up...")
    logger.info("📱 WhatsApp webhook ready at /api/whatsapp/webhook")
    logger.info("🎛️ Admin panel ready at /api/admin")
    logger.info("✅ All systems operational")
    
    yield
    
    # Shutdown
    logger.info("👋 SiteMind API shutting down...")


# =============================================================================
# APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="SiteMind API",
    description="The AI Layer for Construction - WhatsApp-based construction intelligence",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Local dashboard
        "http://localhost:3001",     # Alternative port
        "https://*.vercel.app",      # Vercel deployments
        "https://*.sitemind.ai",     # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROUTES
# =============================================================================

# Include routers
app.include_router(whatsapp_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "SiteMind API",
        "version": "1.0.0",
        "description": "The AI Layer for Construction",
        "status": "operational",
        "endpoints": {
            "whatsapp_webhook": "/api/whatsapp/webhook",
            "admin": "/api/admin",
            "docs": "/docs",
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "gemini": "configured",
            "whatsapp": "configured",
            "storage": "configured",
            "memory": "configured",
        }
    }


# API info
@app.get("/api")
async def api_info():
    """API information"""
    return {
        "version": "1.0.0",
        "endpoints": {
            "whatsapp": {
                "webhook": "POST /api/whatsapp/webhook",
                "send": "POST /api/whatsapp/send",
                "trigger_briefs": "POST /api/whatsapp/trigger-briefs",
            },
            "admin": {
                "onboarding": {
                    "start": "POST /api/admin/onboarding/start",
                    "organization": "POST /api/admin/onboarding/organization",
                    "admin_user": "POST /api/admin/onboarding/admin-user",
                    "project": "POST /api/admin/onboarding/project",
                    "team_members": "POST /api/admin/onboarding/team-members",
                    "complete": "POST /api/admin/onboarding/{session_id}/complete",
                    "quick_setup": "POST /api/admin/quick-setup",
                },
                "config": {
                    "organization": "GET/PUT /api/admin/organizations/{org_id}/config",
                    "project": "GET/PUT /api/admin/projects/{project_id}/config",
                    "user": "GET/PUT /api/admin/users/{user_id}/config",
                },
                "features": {
                    "list": "GET /api/admin/organizations/{org_id}/features",
                    "enable": "POST /api/admin/organizations/{org_id}/features/{feature}/enable",
                    "disable": "POST /api/admin/organizations/{org_id}/features/{feature}/disable",
                },
            },
        }
    }


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if app.debug else None,
        }
    )


# =============================================================================
# SCHEDULED TASKS (Would use APScheduler or Celery in production)
# =============================================================================

async def run_scheduled_tasks():
    """
    Run scheduled tasks
    
    In production, these would be triggered by:
    - Celery beat
    - APScheduler
    - External cron (Railway, Render)
    """
    pass


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
