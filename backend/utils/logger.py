"""
SiteMind Logger
Structured logging with loguru
"""

import sys
from loguru import logger

# Configure loguru
logger.remove()  # Remove default handler

# Console output with colors
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan>: <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# File output for debugging
logger.add(
    "logs/sitemind_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    compression="zip",
)

# Export
__all__ = ["logger"]
