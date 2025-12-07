"""
SiteMind Services
Enterprise Construction Management Platform

CORE SERVICES:
- Gemini AI (Blueprint analysis, multimodal)
- Memory (Supermemory.ai - unlimited context)
- WhatsApp (Twilio - communication layer)
- Storage (Supabase - files + database)

ENTERPRISE FEATURES:
- Red Flag Detection (Proactive risk identification)
- Office-Site Sync (Bridge communication gaps)
- Task Management (Live checklist tracking)
- Progress Monitoring (AI-powered tracking)
- Material Management (Inventory + consumption)
- ROI Tracking (Prove value to clients)
- Automated Reports (Weekly/monthly)
- Subscription Management (Billing + anti-gaming)
"""

from services.gemini_service import GeminiService
from services.memory_service import MemoryService
from services.whatsapp_client import WhatsAppClient
from services.storage_service import StorageService
from services.roi_service import ROIService
from services.report_service import ReportService
from services.subscription_service import SubscriptionService
from services.pricing_service import PricingService
from services.project_lifecycle import ProjectLifecycleService
from services.smart_assistant import SmartAssistantService
from services.engagement_service import EngagementService
from services.red_flag_service import RedFlagService
from services.office_site_sync import OfficeSiteSyncService
from services.task_management import TaskManagementService
from services.progress_monitoring import ProgressMonitoringService
from services.material_management import MaterialManagementService

__all__ = [
    # Core AI
    "GeminiService",
    "MemoryService",
    
    # Communication
    "WhatsAppClient",
    "StorageService",
    
    # Business Logic
    "SubscriptionService",
    "PricingService",
    "ProjectLifecycleService",
    
    # Intelligence
    "SmartAssistantService",
    "RedFlagService",
    
    # Operations
    "OfficeSiteSyncService",
    "TaskManagementService",
    "ProgressMonitoringService",
    "MaterialManagementService",
    
    # Reporting
    "ROIService",
    "ReportService",
    "EngagementService",
]
