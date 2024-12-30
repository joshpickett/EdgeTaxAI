import os
import sys
from api.setup_path import setup_python_path
from datetime import datetime
import uuid

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from flask import jsonify
from plaid.exceptions import PlaidError
from typing import Dict, Any, Tuple
from api.utils.audit_logger import AuditLogger

class APIError(Exception):
    """Custom API Exception class"""
    def __init__(self, message: str, status_code: int = 400, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
        self.timestamp = datetime.now().isoformat()
        self.error_id = str(uuid.uuid4())
        
        # Enhanced error logging
        logging.error(f"API Error {self.error_id}: {message}", extra={
            'status_code': status_code,
            'payload': payload,
            'timestamp': self.timestamp,
            'error_type': self.__class__.__name__
        })

class SessionError(APIError):
    """Session-related errors"""
    def __init__(self, message: str, session_id: str = None):
        super().__init__(message, status_code=401)
        self.session_id = session_id

class RateLimitError(APIError):
    """Rate limit exceeded errors"""
    def __init__(self, message: str, limit: int, window: int):
        super().__init__(
            message, 
            status_code=429,
            payload={
                "limit": limit,
                "window_seconds": window
            }
        )

class ReportGenerationError(APIError):
    """Specific error class for report generation failures"""
    def __init__(self, message: str, report_type: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=500)
        self.report_type = report_type
        self.details = details or {}
        logging.error(f"Report Generation Error: {message} for type {report_type}")

class GigPlatformError(APIError):
    """Specific error class for gig platform operations"""
    def __init__(self, 
                 message: str, 
                 platform: str, 
                 error_code: str = None, 
                 status_code: int = 400):
        super().__init__(message, status_code)
        self.platform = platform
        self.error_code = error_code

def handle_plaid_error(error: PlaidError) -> Tuple[Dict[str, Any], int]:
    """Handle Plaid errors"""
    message = error.message if error.message else "An error occurred"
    return jsonify({
        "error": {
            "message": message
        },
        "status": "error"
    }), 400

def handle_api_error(error: APIError) -> Tuple[Dict[str, Any], int]:
    """Handle custom API errors"""
    audit_logger = AuditLogger()
    
    # Enhanced error tracking
    error_context = {
        'error_id': getattr(error, 'error_id', str(uuid.uuid4())),
        'timestamp': getattr(error, 'timestamp', datetime.now().isoformat()),
        'error_type': error.__class__.__name__,
        'status_code': error.status_code
    }
    
    # Log error details
    audit_logger.log_error(
        error_type="api_error",
        message=error.message,
        details={**error.payload, **error_context}
    )

    response = {
        "error": {
            "message": error.message,
            "code": error.status_code,
            "timestamp": datetime.now().isoformat(),
            **error.payload
        },
        "status": "error"
    }
    return jsonify(response), error.status_code

def handle_platform_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle platform-specific errors"""
    if isinstance(error, requests.exceptions.RequestException):
        return jsonify({
            "error": "Platform API request failed",
            "details": str(error),
            "status": "error"
        }), 503
    elif isinstance(error, TokenError):
        return jsonify({
            "error": "Token error",
            "details": str(error),
            "status": "error"
        }), 401
    elif isinstance(error, ValueError):
        return jsonify({
            "error": "Invalid request",
            "details": str(error),
            "status": "error"
        }), 400

    if isinstance(error, GigPlatformError):
        response = {
            "error": {
                "message": error.message,
                "platform": error.platform,
                "error_code": error.error_code
            },
            "status": "error"
        }
        return jsonify(response), error.status_code
    
    return handle_api_error(APIError(str(error)))

def handle_report_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle report generation specific errors"""
    if isinstance(error, ReportGenerationError):
        response = {
            "error": {
                "message": error.message,
                "report_type": error.report_type,
                "details": error.details
            },
            "status": "error"
        }
        return jsonify(response), error.status_code
    return handle_api_error(APIError(str(error)))
