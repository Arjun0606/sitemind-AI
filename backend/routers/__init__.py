"""
SiteMind API Routers
"""

from routers.whatsapp import router as whatsapp_router
from routers.admin import router as admin_router
from routers.health import router as health_router

__all__ = ["whatsapp_router", "admin_router", "health_router"]
