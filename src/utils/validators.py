import re
from typing import Optional


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format (basic check)."""
    pattern = r'^\+?[\d\s\-\(\)]{10,}$'
    return bool(re.match(pattern, phone))


def is_strong_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None


def is_valid_username(username: str) -> bool:
    """Validate username format (alphanumeric, underscore, hyphen)."""
    pattern = r'^[a-zA-Z0-9_-]{3,30}$'
    return bool(re.match(pattern, username))


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))
