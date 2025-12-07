"""
SiteMind Services
All service classes for the application
"""

# Core AI Services
from services.gemini_service import GeminiService
from services.memory_service import MemoryService

# Communication
from services.whatsapp_client import WhatsAppClient

# Storage
from services.storage_service import StorageService

# Intelligence
from services.smart_assistant import SmartAssistantService, smart_assistant
from services.universal_inbox import UniversalInboxService, universal_inbox, InputType, InputIntent
from services.proactive_intelligence import ProactiveIntelligenceService, proactive_intelligence

# Project Management
from services.task_management import TaskManagementService, task_management, TaskStatus
from services.progress_monitoring import ProgressMonitoringService, progress_monitoring
from services.material_management import MaterialManagementService, material_management

# Monitoring & Alerts
from services.red_flag_service import RedFlagService, red_flag_service
from services.office_site_sync import OfficeSiteSyncService, office_site_sync
from services.engagement_service import EngagementService, engagement_service

# Business
from services.roi_service import ROIService, roi_service

# Customer Management
from services.config_service import ConfigService, config_service
from services.onboarding_service import OnboardingService, onboarding_service
from services.team_management import TeamManagementService, team_management


__all__ = [
    # Core AI
    "GeminiService",
    "MemoryService",
    
    # Communication
    "WhatsAppClient",
    
    # Storage
    "StorageService",
    
    # Intelligence
    "SmartAssistantService",
    "smart_assistant",
    "UniversalInboxService",
    "universal_inbox",
    "InputType",
    "InputIntent",
    "ProactiveIntelligenceService",
    "proactive_intelligence",
    
    # Project Management
    "TaskManagementService",
    "task_management",
    "TaskStatus",
    "ProgressMonitoringService",
    "progress_monitoring",
    "MaterialManagementService",
    "material_management",
    
    # Monitoring & Alerts
    "RedFlagService",
    "red_flag_service",
    "OfficeSiteSyncService",
    "office_site_sync",
    "EngagementService",
    "engagement_service",
    
    # Business
    "ROIService",
    "roi_service",
    
    # Customer Management
    "ConfigService",
    "config_service",
    "OnboardingService",
    "onboarding_service",
    "TeamManagementService",
    "team_management",
]
