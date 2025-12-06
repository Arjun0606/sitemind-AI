"""
SiteMind Configuration Module
Centralized configuration management using Pydantic Settings
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "SiteMind"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/sitemind"
    database_sync_url: str = "postgresql://postgres:password@localhost:5432/sitemind"
    
    # Google Gemini - Using the BEST models at $500/site pricing
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"  # Best model - "thinking" capabilities
    gemini_pro_model: str = "gemini-2.5-pro"  # Same - always use the best
    
    # Supermemory (optional - falls back to in-memory)
    supermemory_api_key: str = ""
    
    # Twilio (WhatsApp)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    
    # Supabase (Database + Storage - all in one!)
    supabase_url: str = ""
    supabase_key: str = ""  # anon/public key
    supabase_service_key: str = ""  # service role key for admin ops
    
    # Sentry
    sentry_dsn: Optional[str] = None
    
    # Rate Limiting
    max_queries_per_user_per_day: int = 50
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
