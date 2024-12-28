import os
from typing import Callable, Any, Optional, Dict, Union
from api.utils.rate_limit import rate_limit
from api.utils.session_manager import SessionManager
from api.utils.token_manager import TokenManager
from api.utils.error_handler import APIError
from api.setup_path import setup_python_path
setup_python_path(__file__)

from functools import wraps
from flask import request, jsonify
import jwt
import redis
from redis.exceptions import RedisError
from datetime import datetime, timedelta
import json
import logging

# Initialize Redis client with error handling
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
except redis.RedisError as e:
    logging.error(f"Failed to initialize Redis client: {str(e)}")
    redis_client = None

# Initialize components
token_manager = TokenManager()  # Initialize at module level
session_manager = SessionManager()  # Initialize at module level
REFRESH_THRESHOLD = 300  # 5 minutes before expiry

class AuthError(APIError):
    """Custom authentication error class"""
    pass

def token_required(function: Callable) -> Callable:
    """Decorator to verify JSON Web Tokens"""
    @wraps(function)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = None
        
        if not os.getenv('JWT_SECRET_KEY'):
            raise AuthError("JWT secret key not configured", 500)

        if 'Authorization' in request.headers:
            authorization_header = request.headers['Authorization']
            try:
                token = authorization_header.split(" ")[1]
            except IndexError:
                raise AuthError("Invalid token format", 401)

            if not validate_token_format(token):
                raise AuthError("Invalid token format", 401)

            # Validate token
            try:
                claims = token_manager.verify_token(token)
                request.user = claims
            except jwt.InvalidTokenError as e:
                if token_manager.can_refresh(token):
                    new_token = token_manager.refresh_token(token)
                    if new_token:
                        response = function(*args, **kwargs)
                        response.headers['New-Token'] = new_token
                        return response
                raise AuthError("Token has expired", 401)

        if not token:
            raise AuthError("Token is missing", 401)

        return function(*args, **kwargs)

    return decorated

def generate_token(user_identifier: int) -> str:
    """Generate JSON Web Token for user"""
    payload = {
        'user_id': user_identifier,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY'),
        algorithm="HS256"
    )

def needs_refresh(token: str) -> bool:
    """Check if token needs to be refreshed"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload['exp'])
        return (exp - datetime.utcnow()).total_seconds() < REFRESH_THRESHOLD
    except:
        return False

def refresh_token(old_token: str) -> Optional[str]:
    """Refresh token if it's approaching expiration"""
    try:
        payload = jwt.decode(old_token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
        return generate_token(payload['user_id'])
    except:
        return None

# Use the rate limit implementation from utils
rate_limit = rate_limit.rate_limit

class APIError(Exception):
    """Custom API Exception"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__()
        self.message = message
        self.status_code = status_code

def handle_api_error(error: APIError) -> tuple:
    """Handle API errors with proper logging and response"""
    logging.error(f"API Error: {error.message}")
    response = {
        "error": error.message,
        "status": "error",
        "timestamp": datetime.utcnow().isoformat()
    }
    return jsonify(response), error.status_code

def validate_token_format(token: str) -> bool:
    """Validate token format"""
    try:
        parts = token.split('.')
        return len(parts) == 3 and all(parts)
    except:
        return False

session_manager = session_manager.SessionManager()

def create_session(user_id: int, device_info: dict) -> str:
    """Create new session with device tracking"""
    try:
        session_data = {
            'user_id': user_id,
            'device_info': device_info or {},
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=session_manager.session_duration)).isoformat()
        }
        if not redis_client:
            raise AuthError("Session storage unavailable", 500)

        if session_manager.create_session(user_id, session_data):
            return session_data.get('session_id')
        return None
    except Exception as e:
        logging.error(f"Error creating session: {e}")
        return None
