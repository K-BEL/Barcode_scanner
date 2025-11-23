"""File utility functions."""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.logging import logger


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
    """
    try:
        if not file_path.exists() or file_path.stat().st_size == 0:
            with open(file_path, "w") as f:
                json.dump({}, f)
            return {}
        
        with open(file_path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.warning(f"Invalid JSON structure in {file_path}, initializing empty dict")
                data = {}
                save_json_file(data, file_path)
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return {}


def save_json_file(data: Dict[str, Any], file_path: Path) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path to the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False


def ensure_directory_exists(directory_path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        The directory path
    """
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path

