from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Optional
import logging
from datetime import datetime, timedelta
from api.utils.token_manager import TokenManager
from api.utils.session_manager import SessionManager
from api.utils.encryption_utils import EncryptionManager
from api.utils.validators import validate_token_format
from api.exceptions.auth_exceptions import AuthError
import os
import jwt

# Initialize components
encryption_manager = EncryptionManager()
session_manager = SessionManager()
token_manager = TokenManager()

REFRESH_THRESHOLD = 300  # 5 minutes before expiry


class AuthError(Exception):
    """Custom authentication error class"""

    pass


def token_required(function: Callable) -> Callable:
    """Decorator to verify JSON Web Tokens"""

    @wraps(function)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = None

        if "Authorization" in request.headers:
            authorization_header = request.headers["Authorization"]
            try:
                token = authorization_header.split(" ")[1]
                if not validate_token_format(token):
                    raise AuthError("Invalid token format")
            except IndexError:
                raise AuthError("Invalid token format", 401)

            # Verify token and session
            claims = token_manager.verify_token(token)
            if not claims:
                raise AuthError("Invalid token")

            # Validate token
            request.user = claims
            logging.info(f"User {claims['user_id']} authenticated successfully.")
            return function(*args, **kwargs)

        if not token:
            raise AuthError("Token is missing", 401)

        return function(*args, **kwargs)

    return decorated


def generate_token(user_identifier: int) -> str:
    """Generate JSON Web Token for user"""
    payload = {
        "user_id": user_identifier,
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")


def needs_refresh(token: str) -> bool:
    """Check if token needs to be refreshed"""
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload["exp"])
        return (exp - datetime.utcnow()).total_seconds() < REFRESH_THRESHOLD
    except:
        return False


def refresh_token(old_token: str) -> Optional[str]:
    """Refresh token if it's approaching expiration"""
    try:
        payload = jwt.decode(
            old_token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"]
        )
        return generate_token(payload["user_id"])
    except:
        return None


def validate_token_format(token: str) -> bool:
    """Validate token format"""
    try:
        parts = token.split(".")
        return len(parts) == 3 and all(parts)
    except:
        return False


def handle_api_error(error: Exception) -> tuple:
    """Handle API errors with proper logging and response"""
    logging.error(f"API Error: {error.message}")
    response = {
        "error": error.message,
        "status": "error",
        "timestamp": datetime.utcnow().isoformat(),
    }
    return jsonify(response), error.status_code
