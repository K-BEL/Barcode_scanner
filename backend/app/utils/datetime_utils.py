"""Utility functions for datetime serialization."""
from datetime import datetime
from typing import Optional, Any


def serialize_datetime(dt: Any) -> str:
    """
    Serialize datetime object to ISO format string.
    
    Args:
        dt: Datetime object or string
        
    Returns:
        ISO format string representation
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        return dt
    
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    
    return str(dt)


def serialize_datetime_optional(dt: Optional[Any]) -> Optional[str]:
    """
    Serialize optional datetime object to ISO format string.
    
    Args:
        dt: Optional datetime object or string
        
    Returns:
        ISO format string representation or None
    """
    if dt is None:
        return None
    
    return serialize_datetime(dt)

