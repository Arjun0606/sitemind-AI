"""
SiteMind Helper Functions
Utility functions used across the application
"""

import re
import uuid
import hashlib
from typing import Optional
from datetime import datetime


def extract_phone_number(whatsapp_from: str) -> str:
    """
    Extract phone number from WhatsApp format
    
    Args:
        whatsapp_from: Phone number in format "whatsapp:+919876543210"
    
    Returns:
        Clean phone number like "+919876543210"
    """
    if whatsapp_from.startswith("whatsapp:"):
        return whatsapp_from.replace("whatsapp:", "")
    return whatsapp_from


def format_phone_number(phone: str) -> str:
    """
    Format phone number to WhatsApp format
    
    Args:
        phone: Phone number like "+919876543210" or "9876543210"
    
    Returns:
        WhatsApp format like "whatsapp:+919876543210"
    """
    # Remove any non-digit characters except +
    clean = re.sub(r'[^\d+]', '', phone)
    
    # Add India country code if not present
    if not clean.startswith('+'):
        if clean.startswith('91') and len(clean) == 12:
            clean = f"+{clean}"
        elif len(clean) == 10:
            clean = f"+91{clean}"
        else:
            clean = f"+{clean}"
    
    return f"whatsapp:{clean}"


def generate_unique_id() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path separators and special characters
    clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    clean = clean.strip('. ')
    # Limit length
    if len(clean) > 200:
        name, ext = clean.rsplit('.', 1) if '.' in clean else (clean, '')
        clean = f"{name[:190]}.{ext}" if ext else name[:200]
    return clean


def calculate_cost(
    gemini_tokens: int = 0,
    whisper_minutes: float = 0,
    whatsapp_messages: int = 0
) -> dict:
    """
    Calculate API costs
    
    Pricing (as of Dec 2024):
    - Gemini 2.0 Flash: $0.075/1M input tokens, $0.30/1M output tokens
    - Gemini 1.5 Pro: $1.25/1M input, $5.00/1M output
    - Whisper: $0.006/minute
    - WhatsApp: ~$0.005 per message (varies by country)
    
    Args:
        gemini_tokens: Total tokens used (input + output estimated)
        whisper_minutes: Minutes of audio transcribed
        whatsapp_messages: Number of WhatsApp messages
    
    Returns:
        Dict with cost breakdown
    """
    # Approximate costs (conservative estimates)
    gemini_cost = (gemini_tokens / 1_000_000) * 0.20  # Blended rate
    whisper_cost = whisper_minutes * 0.006
    whatsapp_cost = whatsapp_messages * 0.006  # Average send + receive
    
    return {
        "gemini_cost": round(gemini_cost, 4),
        "whisper_cost": round(whisper_cost, 4),
        "whatsapp_cost": round(whatsapp_cost, 4),
        "total_cost": round(gemini_cost + whisper_cost + whatsapp_cost, 4)
    }


def get_file_hash(content: bytes) -> str:
    """
    Generate SHA256 hash of file content
    
    Args:
        content: File content as bytes
    
    Returns:
        SHA256 hash string
    """
    return hashlib.sha256(content).hexdigest()


def format_response_time(ms: int) -> str:
    """
    Format response time for display
    
    Args:
        ms: Milliseconds
    
    Returns:
        Human-readable string like "2.5s" or "850ms"
    """
    if ms >= 1000:
        return f"{ms / 1000:.1f}s"
    return f"{ms}ms"


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to max length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def parse_drawing_reference(text: str) -> Optional[dict]:
    """
    Parse drawing references from text
    
    Examples:
        "See Drawing ST-04, Grid B2" -> {"drawing": "ST-04", "grid": "B2"}
        "Refer to AR-01 for details" -> {"drawing": "AR-01"}
    
    Args:
        text: Text containing drawing reference
    
    Returns:
        Dict with parsed reference or None
    """
    # Pattern for drawing numbers like ST-04, AR-01, MEP-12
    drawing_pattern = r'\b([A-Z]{2,4}[-_]?\d{1,3})\b'
    # Pattern for grid references like B2, A1-C3
    grid_pattern = r'\bGrid\s+([A-Z]\d(?:[-_][A-Z]\d)?)\b'
    
    result = {}
    
    drawing_match = re.search(drawing_pattern, text)
    if drawing_match:
        result["drawing"] = drawing_match.group(1)
    
    grid_match = re.search(grid_pattern, text, re.IGNORECASE)
    if grid_match:
        result["grid"] = grid_match.group(1)
    
    return result if result else None


def is_rate_limited(
    current_count: int, 
    max_count: int, 
    last_query_date: Optional[datetime] = None
) -> tuple[bool, int]:
    """
    Check if user is rate limited
    
    Args:
        current_count: Current query count
        max_count: Maximum allowed queries
        last_query_date: Date of last query
    
    Returns:
        Tuple of (is_limited, remaining_queries)
    """
    today = datetime.now().date()
    
    # Reset count if it's a new day
    if last_query_date and last_query_date.date() < today:
        return (False, max_count)
    
    remaining = max_count - current_count
    return (remaining <= 0, max(0, remaining))

