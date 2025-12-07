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
    
    # Google Gemini 3.0 Pro - State of the art reasoning
    # https://ai.google.dev/gemini-api/docs/gemini-3
    google_api_key: str = ""
    gemini_model: str = "gemini-3-pro-preview"  # Gemini 3.0 - best reasoning
    gemini_pro_model: str = "gemini-3-pro-preview"  # Same - always use the best
    
    # Gemini 3.0 specific settings
    gemini_thinking_level: str = "high"  # low, medium, high - controls reasoning depth
    gemini_media_resolution: str = "high"  # low, medium, high, ultra_high for blueprints
    
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
    
    # Rate Limiting - UNLIMITED at $500/site but track for analytics
    max_queries_per_user_per_day: int = 999999  # Effectively unlimited
    
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
