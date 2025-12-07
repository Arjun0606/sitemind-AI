"""
SiteMind Logger
Structured logging configuration
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "sitemind", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if already set up
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


# Main logger instance
logger = setup_logger()
