"""
SiteMind Configuration
Centralized settings management using Pydantic Settings

All secrets loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # ==========================================================================
    # APP SETTINGS
    # ==========================================================================
    APP_NAME: str = "SiteMind"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ==========================================================================
    # GOOGLE GEMINI
    # ==========================================================================
    GOOGLE_API_KEY: str = "your_google_api_key"
    GEMINI_MODEL: str = "gemini-2.0-flash"  # Fast responses
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"  # Complex analysis
    
    # ==========================================================================
    # SUPERMEMORY (Long-term memory)
    # ==========================================================================
    SUPERMEMORY_API_KEY: str = "your_supermemory_api_key"
    
    # ==========================================================================
    # TWILIO (WhatsApp)
    # ==========================================================================
    TWILIO_ACCOUNT_SID: str = "your_twilio_account_sid"
    TWILIO_AUTH_TOKEN: str = "your_twilio_auth_token"
    TWILIO_WHATSAPP_NUMBER: str = "+14155238886"  # Twilio sandbox
    
    # ==========================================================================
    # SUPABASE (Database + Storage)
    # ==========================================================================
    SUPABASE_URL: str = "your_supabase_url"
    SUPABASE_KEY: str = "your_supabase_anon_key"
    SUPABASE_SERVICE_KEY: str = "your_supabase_service_key"
    
    # ==========================================================================
    # DATABASE
    # ==========================================================================
    DATABASE_URL: str = "postgresql://localhost:5432/sitemind"
    
    # ==========================================================================
    # STORAGE
    # ==========================================================================
    STORAGE_BUCKET: str = "sitemind-files"
    
    # ==========================================================================
    # SECURITY
    # ==========================================================================
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==========================================================================
    # FEATURES
    # ==========================================================================
    ENABLE_MORNING_BRIEFS: bool = True
    ENABLE_RED_FLAGS: bool = True
    ENABLE_TASK_MANAGEMENT: bool = True
    ENABLE_MATERIAL_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
