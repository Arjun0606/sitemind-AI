"""
SiteMind Logging Configuration
Uses loguru for structured logging
"""

import sys
from loguru import logger
from config import settings


def setup_logging():
    """Configure logging for the application"""
    
    # Remove default logger
    logger.remove()
    
    # Console logging format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=console_format,
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
    )
    
    # File logging (JSON format for production)
    if settings.is_production:
        logger.add(
            "logs/sitemind_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # New file every midnight
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress old logs
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            level="INFO",
            serialize=True,  # JSON format
        )
    
    logger.info(f"Logging configured for {settings.app_env} environment")
    
    return logger


# Export configured logger
__all__ = ["logger", "setup_logging"]

