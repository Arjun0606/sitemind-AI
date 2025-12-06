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
    
    # Google Gemini
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # Fast model for quick queries
    gemini_pro_model: str = "gemini-1.5-pro"  # Pro model for complex queries
    
    # OpenAI (Whisper)
    openai_api_key: str = ""
    whisper_model: str = "whisper-1"
    
    # Supermemory
    supermemory_api_key: str = ""
    
    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    
    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = "sitemind-blueprints"
    aws_region: str = "ap-south-1"
    
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
