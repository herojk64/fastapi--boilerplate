from datetime import datetime, timedelta, timezone
from typing import Optional


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(dt_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime string."""
    try:
        return datetime.strptime(dt_string, format_str)
    except ValueError:
        return None


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to datetime."""
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """Add hours to datetime."""
    return dt + timedelta(hours=hours)


def is_expired(dt: datetime) -> bool:
    """Check if datetime has expired (is in the past)."""
    return dt < utc_now()


def time_until_expiry(dt: datetime) -> timedelta:
    """Get time remaining until expiry."""
    return dt - utc_now()


def human_readable_time(dt: datetime) -> str:
    """Convert datetime to human-readable format (e.g., '2 hours ago')."""
    now = utc_now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return format_datetime(dt, "%b %d, %Y")
