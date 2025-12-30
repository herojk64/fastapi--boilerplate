import re
import secrets
import string
from typing import Optional


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def generate_random_string(length: int = 32, include_punctuation: bool = False) -> str:
    """Generate cryptographically secure random string."""
    chars = string.ascii_letters + string.digits
    if include_punctuation:
        chars += string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_token(length: int = 32) -> str:
    """Generate URL-safe token."""
    return secrets.token_urlsafe(length)


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def mask_email(email: str) -> str:
    """Mask email address for privacy (e.g., u***@example.com)."""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def extract_filename_from_path(path: str) -> str:
    """Extract filename from file path."""
    return path.split('/')[-1]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing unsafe characters."""
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')
