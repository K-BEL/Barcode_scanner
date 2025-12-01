"""Input validation utilities."""
import re
from typing import Optional


def validate_barcode(barcode: str) -> str:
    """
    Validate barcode format.
    
    Barcodes should be:
    - Non-empty
    - Alphanumeric (letters, numbers, and common barcode characters like -)
    - Max 255 characters (database limit)
    - Not just whitespace
    
    Args:
        barcode: Barcode string to validate
        
    Returns:
        Stripped barcode string
        
    Raises:
        ValueError: If barcode format is invalid
    """
    if not barcode:
        raise ValueError("Barcode cannot be empty")
    
    barcode = barcode.strip()
    
    if not barcode:
        raise ValueError("Barcode cannot be whitespace only")
    
    if len(barcode) > 255:
        raise ValueError("Barcode cannot exceed 255 characters")
    
    # Allow alphanumeric and common barcode characters (-, _, spaces)
    # Most barcodes are numeric, but some formats allow letters
    if not re.match(r'^[A-Za-z0-9\-\s_]+$', barcode):
        raise ValueError("Barcode contains invalid characters. Only alphanumeric, hyphens, underscores, and spaces are allowed")
    
    return barcode


def validate_user_id(user_id: str) -> str:
    """
    Validate user ID format.
    
    Args:
        user_id: User ID string to validate
        
    Returns:
        Stripped user ID string
        
    Raises:
        ValueError: If user ID format is invalid
    """
    if not user_id:
        raise ValueError("User ID cannot be empty")
    
    user_id = user_id.strip()
    
    if not user_id:
        raise ValueError("User ID cannot be whitespace only")
    
    if len(user_id) > 36:  # UUID format
        raise ValueError("User ID cannot exceed 36 characters")
    
    return user_id

