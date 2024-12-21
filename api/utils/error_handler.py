import logging
from flask import jsonify
from plaid.exceptions import PlaidError
from typing import Dict, Any, Tuple

class APIError(Exception):
    """Custom API Exception class"""
    def __init__(self, message: str, status_code: int = 400, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

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
    response = {
        "error": {
            "message": error.message,
            **error.payload
        },
        "status": "error"
    }
    return jsonify(response), error.status_code
