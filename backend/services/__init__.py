"""
SiteMind Services
Core AI and business logic services

TECH STACK:
- Gemini 3.0 Pro (State-of-the-art AI)
- Supermemory.ai (Unlimited project context)
- Twilio (WhatsApp)
- Supabase (Database + Storage)

BUSINESS SERVICES:
- ROI Tracking (Proves value to builders)
- Automated Reports (Weekly/Monthly)
- Pricing (Active sites + Archive upsell)
- Project Lifecycle (Onboarding → Archive)

ENGAGEMENT (Make it ADDICTIVE):
- Smart Assistant (Language, typos, context)
- Engagement Service (Streaks, milestones, summaries)
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
from services.smart_assistant import SmartAssistant
from services.engagement_service import EngagementService

__all__ = [
    "GeminiService",
    "MemoryService",
    "WhatsAppClient",
    "StorageService",
    "ROIService",
    "ReportService",
    "SubscriptionService",
    "PricingService",
    "ProjectLifecycleService",
    "SmartAssistant",
    "EngagementService",
]
