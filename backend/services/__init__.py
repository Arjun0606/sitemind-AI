"""
SiteMind Services
Complete service layer for the $100k/month product
"""

# Core AI
from services.gemini_service import gemini_service
from services.memory_service import memory_service
from services.intelligence_service import intelligence_service

# Communication
from services.whatsapp_service import whatsapp_service

# Storage
from services.storage_service import storage_service

# Business
from services.pricing_service import pricing_service
from services.billing_service import billing_service

# Engagement
from services.wow_service import wow_service
from services.daily_brief_service import daily_brief_service
from services.report_service import report_service
from services.alert_service import alert_service

# Project Management
from services.project_manager import project_manager
from services.command_handler import command_handler

# Subscription & Billing
from services.subscription_reminder_service import subscription_reminder_service

# THE SIMPLE CORE - This is all you need
from services.sitemind_core import sitemind_core
from services.document_ingestion_service import document_ingestion_service

# Legacy services (kept for backwards compatibility)
from services.leakage_prevention_service import leakage_prevention_service
from services.office_sync_service import office_sync_service
from services.ultimate_leakage_engine import ultimate_leakage_engine
from services.material_tracker_service import material_tracker_service

__all__ = [
    # Core AI
    "gemini_service",
    "memory_service",
    "intelligence_service",
    
    # Communication
    "whatsapp_service",
    
    # Storage
    "storage_service",
    
    # Business
    "pricing_service",
    "billing_service",
    
    # Engagement
    "wow_service",
    "daily_brief_service",
    "report_service",
    "alert_service",
    
    # Project Management
    "project_manager",
    "command_handler",
    
    # Subscription & Billing
    "subscription_reminder_service",
    
    # THE SIMPLE CORE
    "sitemind_core",
    "document_ingestion_service",
    
    # Legacy services
    "leakage_prevention_service",
    "office_sync_service",
    "ultimate_leakage_engine",
    "material_tracker_service",
]
