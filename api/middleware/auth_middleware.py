from functools import wraps
from flask import request, jsonify
from typing import Callable, Any
from api.models.users import Users
from api.config.database import SessionLocal
import jwt
import logging
from datetime import datetime, timedelta
import os

# Direct imports from utils
from api.utils.token_manager import TokenManager
from api.utils.session_manager import SessionManager
from api.utils.error_handler import AuthError, handle_api_error
from api.utils.audit_trail import AuditLogger

# Initialize components
token_manager = TokenManager()
session_manager = SessionManager()
audit_logger = AuditLogger()
REFRESH_THRESHOLD = 300  # 5 minutes before expiry

class AuthError(APIError):
    """Custom authentication error class"""
    pass

def token_required(function: Callable) -> Callable:
    """Decorator to verify JSON Web Tokens"""
    @wraps(function)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = None
        
        if 'Authorization' in request.headers:
            authorization_header = request.headers['Authorization']
            try:
                token = authorization_header.split(" ")[1]
            except IndexError:
                raise AuthError("Invalid token format", 401)

            # Get user from database
            db = SessionLocal()
            claims = token_manager.verify_token(token)
            user = db.query(Users).filter(Users.id == claims['user_id']).first()
            if not user:
                raise AuthError("User not found", 401)

            # Validate token
            try:
                claims = token_manager.verify_token(token)
                request.user = claims
                audit_logger.log_auth_success(claims['user_id'], 'token_verification')
                return function(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                audit_logger.log_auth_failure(claims.get('user_id'), 'token_expired')
                if token_manager.can_refresh(token):
                    new_token = token_manager.refresh_token(token)
                    if new_token:
                        response = function(*args, **kwargs)
                        response.headers['New-Token'] = new_token
                        return response
                raise AuthError("Token has expired", 401)
            except jwt.InvalidTokenError:
                raise AuthError("Invalid token", 401)

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

def validate_token_format(token: str) -> bool:
    """Validate token format"""
    try:
        parts = token.split('.')
        return len(parts) == 3 and all(parts)
    except:
        return False

def handle_api_error(error: APIError) -> tuple:
    """Handle API errors with proper logging and response"""
    logging.error(f"API Error: {error.message}")
    response = {
        "error": error.message,
        "status": "error",
        "timestamp": datetime.utcnow().isoformat()
    }
    return jsonify(response), error.status_code
