"""
SiteMind - AI Site Engineer
Main FastAPI Application Entry Point

"The AI Site Engineer - Fleetline for Construction"
"""

import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from config import settings
from utils.logger import setup_logging, logger
from utils.database import init_db, close_db
from routers.whatsapp import router as whatsapp_router
from routers.admin import router as admin_router
from routers.analytics import router as analytics_router
from services.gemini_service import gemini_service
from services.whatsapp_client import whatsapp_client
from services.memory_service import memory_service
from services.storage_service import storage_service


# ===========================================
# Application Lifespan
# ===========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Manages startup and shutdown events
    """
    # Startup
    logger.info("🏗️  Starting SiteMind...")
    
    # Setup logging
    setup_logging()
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Log service status
    logger.info(f"🤖 Gemini 2.5 Pro: {'✅ Ready' if gemini_service.is_configured else '❌ Not configured'}")
    logger.info(f"💬 WhatsApp: {'✅ Ready' if whatsapp_client.is_configured else '❌ Not configured'}")
    logger.info(f"🧠 Memory: {'✅ Ready' if memory_service.is_configured else '⚠️ Using fallback'}")
    logger.info(f"📁 Supabase Storage: {'✅ Ready' if storage_service.is_configured else '❌ Not configured'}")
    
    logger.info("🚀 SiteMind is ready to serve!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down SiteMind...")
    await close_db()
    logger.info("👋 Goodbye!")


# ===========================================
# Initialize Sentry (Error Tracking)
# ===========================================

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.app_env,
    )


# ===========================================
# Create FastAPI Application
# ===========================================

app = FastAPI(
    title="SiteMind API",
    description="""
    🏗️ **SiteMind - The AI Site Engineer**
    
    SiteMind is an AI-powered assistant for construction site engineers.
    It reads blueprints, remembers project history, and answers questions instantly via WhatsApp.
    
    ## Features
    
    * 📐 **Blueprint Analysis** - Ask questions about any drawing (Gemini 2.5 Pro)
    * 📷 **Site Photos** - Upload photos to verify against blueprints
    * 🧠 **Project Memory** - Remembers RFIs, change orders, and decisions
    
    ## Quick Links
    
    * [Admin Dashboard](/docs#/Admin) - Manage projects and engineers
    * [Analytics](/docs#/Analytics) - View usage statistics
    * [WhatsApp Webhook](/docs#/WhatsApp) - Webhook endpoints
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ===========================================
# CORS Middleware
# ===========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [
        "https://sitemind.ai",
        "https://admin.sitemind.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# Global Exception Handler
# ===========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again.",
            "error_id": str(id(exc)),
        }
    )


# ===========================================
# Include Routers
# ===========================================

app.include_router(whatsapp_router)
app.include_router(admin_router)
app.include_router(analytics_router)


# ===========================================
# Root Endpoints
# ===========================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - service info"""
    return {
        "service": "SiteMind API",
        "version": "1.0.0",
        "status": "running",
        "tagline": "The AI Site Engineer - Fleetline for Construction",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns status of all services
    """
    gemini_health = await gemini_service.health_check()
    whatsapp_health = await whatsapp_client.health_check()
    memory_health = await memory_service.health_check()
    storage_health = await storage_service.health_check()
    
    all_healthy = all([
        gemini_health.get("status") in ["healthy", "not_configured"],
        whatsapp_health.get("status") in ["healthy", "not_configured"],
        memory_health.get("status") in ["healthy", "fallback"],
        storage_health.get("status") in ["healthy", "not_configured"],
    ])
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": "1.0.0",
        "stack": "Gemini 2.5 Pro + Supabase + Twilio",
        "services": {
            "gemini": gemini_health,
            "whatsapp": whatsapp_health,
            "memory": memory_health,
            "storage": storage_health,
        }
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint for uptime monitoring"""
    return {"pong": True}


# ===========================================
# Run with Uvicorn (for development)
# ===========================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="debug" if settings.debug else "info",
    )

