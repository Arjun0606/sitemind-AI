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
    # PRICING (per company, unlimited projects)
    # ==========================================================================
    FLAT_FEE_USD: float = 1000.0
    QUERY_PRICE_USD: float = 0.20      # 90% margin
    DOCUMENT_PRICE_USD: float = 4.00   # 90% margin
    PHOTO_PRICE_USD: float = 0.80      # 90% margin
    STORAGE_PRICE_USD: float = 0.25    # 92% margin
    
    # ==========================================================================
    # INCLUDED LIMITS (per company)
    # ==========================================================================
    INCLUDED_QUERIES: int = 1000
    INCLUDED_DOCUMENTS: int = 50
    INCLUDED_PHOTOS: int = 200
    INCLUDED_STORAGE_GB: int = 25
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars


# Singleton
settings = Settings()
