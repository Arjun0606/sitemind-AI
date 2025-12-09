"""
SiteMind Services - CLEAN VERSION
=================================

Services are lazy-loaded to prevent startup failures.
"""

from utils.logger import logger

# =============================================================================
# LAZY IMPORTS - Only load when needed
# =============================================================================

_gemini_service = None
_memory_service = None
_storage_service = None
_whatsapp_service = None
_memory_engine = None
_awareness_engine = None
_intelligence_engine = None
_billing_service = None
_pricing_service = None
_project_manager = None
_subscription_reminder_service = None


def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        from services.gemini_service import gemini_service
        _gemini_service = gemini_service
    return _gemini_service


def get_memory_service():
    global _memory_service
    if _memory_service is None:
        from services.memory_service import memory_service
        _memory_service = memory_service
    return _memory_service


def get_storage_service():
    global _storage_service
    if _storage_service is None:
        from services.storage_service import storage_service
        _storage_service = storage_service
    return _storage_service


def get_whatsapp_service():
    global _whatsapp_service
    if _whatsapp_service is None:
        from services.whatsapp_service import whatsapp_service
        _whatsapp_service = whatsapp_service
    return _whatsapp_service


def get_memory_engine():
    global _memory_engine
    if _memory_engine is None:
        from services.phase1_memory_engine import memory_engine
        _memory_engine = memory_engine
    return _memory_engine


def get_awareness_engine():
    global _awareness_engine
    if _awareness_engine is None:
        from services.phase2_awareness_engine import awareness_engine
        _awareness_engine = awareness_engine
    return _awareness_engine


def get_intelligence_engine():
    global _intelligence_engine
    if _intelligence_engine is None:
        from services.phase3_intelligence_engine import intelligence_engine
        _intelligence_engine = intelligence_engine
    return _intelligence_engine


def get_billing_service():
    global _billing_service
    if _billing_service is None:
        from services.billing_service import billing_service
        _billing_service = billing_service
    return _billing_service


def get_pricing_service():
    global _pricing_service
    if _pricing_service is None:
        from services.pricing_service import pricing_service
        _pricing_service = pricing_service
    return _pricing_service


def get_project_manager():
    global _project_manager
    if _project_manager is None:
        from services.project_manager import project_manager
        _project_manager = project_manager
    return _project_manager


def get_subscription_reminder_service():
    global _subscription_reminder_service
    if _subscription_reminder_service is None:
        from services.subscription_reminder_service import subscription_reminder_service
        _subscription_reminder_service = subscription_reminder_service
    return _subscription_reminder_service


# =============================================================================
# DIRECT IMPORTS (for backwards compatibility)
# =============================================================================

# These will be loaded when accessed
try:
    from services.gemini_service import gemini_service
    logger.info("✅ Gemini service loaded")
except Exception as e:
    logger.warning(f"⚠️ Gemini service not loaded: {e}")
    gemini_service = None

try:
    from services.memory_service import memory_service
    logger.info("✅ Memory service loaded")
except Exception as e:
    logger.warning(f"⚠️ Memory service not loaded: {e}")
    memory_service = None

try:
    from services.storage_service import storage_service
    logger.info("✅ Storage service loaded")
except Exception as e:
    logger.warning(f"⚠️ Storage service not loaded: {e}")
    storage_service = None

try:
    from services.whatsapp_service import whatsapp_service
    logger.info("✅ WhatsApp service loaded")
except Exception as e:
    logger.warning(f"⚠️ WhatsApp service not loaded: {e}")
    whatsapp_service = None

try:
    from services.phase1_memory_engine import memory_engine
    logger.info("✅ Memory engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Memory engine not loaded: {e}")
    memory_engine = None

try:
    from services.phase2_awareness_engine import awareness_engine
    logger.info("✅ Awareness engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Awareness engine not loaded: {e}")
    awareness_engine = None

try:
    from services.phase3_intelligence_engine import intelligence_engine
    logger.info("✅ Intelligence engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Intelligence engine not loaded: {e}")
    intelligence_engine = None

try:
    from services.billing_service import billing_service
    logger.info("✅ Billing service loaded")
except Exception as e:
    logger.warning(f"⚠️ Billing service not loaded: {e}")
    billing_service = None

try:
    from services.pricing_service import pricing_service
    logger.info("✅ Pricing service loaded")
except Exception as e:
    logger.warning(f"⚠️ Pricing service not loaded: {e}")
    pricing_service = None

try:
    from services.project_manager import project_manager
    logger.info("✅ Project manager loaded")
except Exception as e:
    logger.warning(f"⚠️ Project manager not loaded: {e}")
    project_manager = None

try:
    from services.subscription_reminder_service import subscription_reminder_service
    logger.info("✅ Subscription reminder loaded")
except Exception as e:
    logger.warning(f"⚠️ Subscription reminder not loaded: {e}")
    subscription_reminder_service = None

logger.info("🚀 SiteMind services initialized")


__all__ = [
    "gemini_service",
    "memory_service",
    "storage_service",
    "whatsapp_service",
    "memory_engine",
    "awareness_engine",
    "intelligence_engine",
    "billing_service",
    "pricing_service",
    "project_manager",
    "subscription_reminder_service",
    # Getters
    "get_gemini_service",
    "get_memory_service",
    "get_storage_service",
    "get_whatsapp_service",
    "get_memory_engine",
    "get_awareness_engine",
    "get_intelligence_engine",
    "get_billing_service",
    "get_pricing_service",
    "get_project_manager",
    "get_subscription_reminder_service",
]
