"""
SiteMind Configuration
All settings loaded from environment variables

SETUP:
1. Copy .env.example to .env
2. Fill in your API keys
3. Run the app!
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # ==========================================================================
    # APP
    # ==========================================================================
    APP_NAME: str = "SiteMind"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ==========================================================================
    # GOOGLE GEMINI (AI)
    # ==========================================================================
    # Get from: https://makersuite.google.com/app/apikey
    GOOGLE_API_KEY: str = "your_google_api_key"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # ==========================================================================
    # SUPERMEMORY (Long-term memory)
    # ==========================================================================
    # Get from: https://supermemory.ai/dashboard
    # Docs: https://supermemory.ai/docs/introduction
    SUPERMEMORY_API_KEY: str = "your_supermemory_api_key"
    
    # ==========================================================================
    # SUPABASE (Database + Storage)
    # ==========================================================================
    # Get from: https://app.supabase.com/project/YOUR_PROJECT/settings/api
    SUPABASE_URL: str = "your_supabase_url"
    SUPABASE_KEY: str = "your_supabase_anon_key"
    SUPABASE_SERVICE_KEY: str = "your_supabase_service_key"
    
    # ==========================================================================
    # TWILIO (WhatsApp)
    # ==========================================================================
    # Get from: https://console.twilio.com
    TWILIO_ACCOUNT_SID: str = "your_twilio_account_sid"
    TWILIO_AUTH_TOKEN: str = "your_twilio_auth_token"
    TWILIO_WHATSAPP_NUMBER: str = "+14155238886"  # Sandbox number
    
    # ==========================================================================
    # SECURITY
    # ==========================================================================
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # ==========================================================================
    # PRICING
    # ==========================================================================
    FLAT_FEE_USD: float = 500.0
    QUERY_PRICE_USD: float = 0.15
    DOCUMENT_PRICE_USD: float = 2.50
    PHOTO_PRICE_USD: float = 0.50
    STORAGE_PRICE_USD: float = 1.00
    
    # ==========================================================================
    # INCLUDED LIMITS
    # ==========================================================================
    INCLUDED_QUERIES: int = 500
    INCLUDED_DOCUMENTS: int = 20
    INCLUDED_PHOTOS: int = 100
    INCLUDED_STORAGE_GB: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars


# Singleton
settings = Settings()
