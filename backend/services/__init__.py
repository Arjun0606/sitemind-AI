"""
SiteMind Services
Enterprise Construction Intelligence Platform

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- GeminiService: Blueprint analysis, multimodal AI
- MemoryService: Supermemory.ai - unlimited context
- SmartAssistantService: Language processing, intent detection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNIVERSAL INBOX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- UniversalInboxService: Process ANY input type
- WhatsAppClient: Communication layer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROACTIVE INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- ProactiveIntelligenceService: Morning briefs, smart alerts
- RedFlagService: Risk detection before problems occur

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- OfficeSiteSyncService: Bridge office-site communication
- TaskManagementService: Live task tracking via WhatsApp
- ProgressMonitoringService: AI progress tracking
- MaterialManagementService: Inventory & consumption

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTEGRATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- IntegrationHub: Connect Google Drive, SAP, Primavera, etc.
- StorageService: Supabase file storage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUSINESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- SubscriptionService: Multi-tenant billing
- PricingService: Volume discounts, pilots
- ProjectLifecycleService: Active → Completed → Archived
- ROIService: Value tracking for clients
- ReportService: Automated reports
- EngagementService: Professional metrics tracking
"""

# Core AI
from services.gemini_service import GeminiService
from services.memory_service import MemoryService
from services.smart_assistant import SmartAssistantService

# Universal Inbox
from services.universal_inbox import UniversalInboxService
from services.whatsapp_client import WhatsAppClient

# Proactive Intelligence
from services.proactive_intelligence import ProactiveIntelligenceService
from services.red_flag_service import RedFlagService

# Operations
from services.office_site_sync import OfficeSiteSyncService
from services.task_management import TaskManagementService
from services.progress_monitoring import ProgressMonitoringService
from services.material_management import MaterialManagementService

# Integrations
from services.integration_hub import IntegrationHub
from services.storage_service import StorageService

# Business
from services.subscription_service import SubscriptionService
from services.pricing_service import PricingService
from services.project_lifecycle import ProjectLifecycleService
from services.roi_service import ROIService
from services.report_service import ReportService
from services.engagement_service import EngagementService

# Customer Management
from services.config_service import ConfigService
from services.onboarding_service import OnboardingService
from services.team_management import TeamManagementService


__all__ = [
    # Core AI
    "GeminiService",
    "MemoryService",
    "SmartAssistantService",
    
    # Universal Inbox
    "UniversalInboxService",
    "WhatsAppClient",
    
    # Proactive Intelligence
    "ProactiveIntelligenceService",
    "RedFlagService",
    
    # Operations
    "OfficeSiteSyncService",
    "TaskManagementService",
    "ProgressMonitoringService",
    "MaterialManagementService",
    
    # Integrations
    "IntegrationHub",
    "StorageService",
    
    # Business
    "SubscriptionService",
    "PricingService",
    "ProjectLifecycleService",
    "ROIService",
    "ReportService",
    "EngagementService",
    
    # Customer Management
    "ConfigService",
    "OnboardingService",
    "TeamManagementService",
]
