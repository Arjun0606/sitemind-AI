"""
SiteMind Services - CLEAN VERSION
=================================

ONLY essential services. No overpromising.

ESSENTIAL SERVICES:
1. gemini_service - AI engine (Gemini 3 Pro)
2. memory_service - Long-term memory (Supermemory)
3. storage_service - File storage (Supabase)
4. whatsapp_service - WhatsApp API
5. phase1_memory_engine - Messages, decisions, RFIs, drawings
6. phase2_awareness_engine - Q&A, issues, progress
7. phase3_intelligence_engine - Reports, predictions
8. billing_service - Usage tracking
9. pricing_service - Pricing logic
10. project_manager - Multi-project support
11. subscription_reminder_service - Payment reminders

REMOVED (overpromising or redundant):
- connected_intelligence.py - Overpromised CV
- sitemind_core.py - Redundant
- document_ingestion_service.py - Overpromised PDF analysis
- watchdog_service.py - Overpromised detection
- ultimate_leakage_engine.py - Overpromised
- leakage_prevention_service.py - Redundant
- material_tracker_service.py - Overpromised
- intelligence_service.py - Redundant
- roi_service.py - Overpromised
- And many more...
"""

from utils.logger import logger

# =============================================================================
# CORE AI SERVICE
# =============================================================================
from services.gemini_service import gemini_service
logger.info("✅ Gemini service loaded")

# =============================================================================
# MEMORY & STORAGE
# =============================================================================
from services.memory_service import memory_service
logger.info("✅ Memory service loaded")

from services.storage_service import storage_service
logger.info("✅ Storage service loaded")

# =============================================================================
# COMMUNICATION
# =============================================================================
from services.whatsapp_service import whatsapp_service
logger.info("✅ WhatsApp service loaded")

# =============================================================================
# PHASE ENGINES (Core functionality)
# =============================================================================
from services.phase1_memory_engine import memory_engine
logger.info("✅ Phase 1: Memory Engine loaded")

from services.phase2_awareness_engine import awareness_engine
logger.info("✅ Phase 2: Awareness Engine loaded")

from services.phase3_intelligence_engine import intelligence_engine
logger.info("✅ Phase 3: Intelligence Engine loaded")

# =============================================================================
# BUSINESS LOGIC
# =============================================================================
from services.billing_service import billing_service
logger.info("✅ Billing service loaded")

from services.pricing_service import pricing_service
logger.info("✅ Pricing service loaded")

from services.project_manager import project_manager
logger.info("✅ Project manager loaded")

from services.subscription_reminder_service import subscription_reminder_service
logger.info("✅ Subscription reminder service loaded")

# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    # Core
    "gemini_service",
    "memory_service",
    "storage_service",
    "whatsapp_service",
    
    # Phase Engines
    "memory_engine",
    "awareness_engine",
    "intelligence_engine",
    
    # Business
    "billing_service",
    "pricing_service",
    "project_manager",
    "subscription_reminder_service",
]

logger.info("🚀 SiteMind services initialized (clean version)")
