"""
Error handling utilities for desktop application
"""
from desktop.setup_path import setup_desktop_path
setup_desktop_path()

import logging
from typing import Optional, Dict, Any
from requests.exceptions import RequestException

def handle_api_error(error: Exception) -> Dict[str, Any]:
    """
    Handle API errors and return appropriate response
    """
    if isinstance(error, RequestException):
        logging.error(f"API Request error: {error}")
        return {
            "status": "error",
            "message": "Failed to connect to API service",
            "error": str(error)
        }
    
    logging.error(f"Unexpected error: {error}")
    return {
        "status": "error",
        "message": "An unexpected error occurred",
        "error": str(error)
    }

def log_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Log error with context
    """
    if context:
        logging.error(f"{context}: {error}")
    else:
        logging.error(f"Error occurred: {error}")
