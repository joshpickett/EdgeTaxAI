from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Optional
import jwt
import redis
from datetime import datetime, timedelta
import os
import json
import logging

# Initialize Redis for token storage
redis_client = redis.Redis(host='localhost', port=6379, db=0)
REFRESH_THRESHOLD = 300  # 5 minutes before expiry

def token_required(function: Callable) -> Callable:
    """Decorator to verify JSON Web Tokens"""
    @wraps(function)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            authorization_header = request.headers['Authorization']
            try:
                token = authorization_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

            # Check if token needs refresh
            if needs_refresh(token):
                new_token = refresh_token(token)
                if new_token:
                    response = function(*args, **kwargs)
                    response.headers['New-Token'] = new_token
                    return response

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Verify token
            data = jwt.decode(
                token, 
                os.getenv('JWT_SECRET_KEY'), 
                algorithms=["HS256"]
            )
            
            # Add user data to request
            request.user = data
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

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

def rate_limit(requests_per_minute: int) -> Callable:
    """Rate limiting decorator"""
    def decorator(function: Callable) -> Callable:
        bucket_name = f"rate_limit:{function.__name__}"
        
        @wraps(function)
        def decorated_function(*args: Any, **kwargs: Any):
            client_ip = request.remote_addr
            key = f"{bucket_name}:{client_ip}"
            
            # Get current request count
            current = redis_client.get(key)
            if current is None:
                redis_client.setex(key, 60, 1)
            elif int(current) >= requests_per_minute:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": redis_client.ttl(key)
                }), 429
            else:
                redis_client.incr(key)
                
            return function(*args, **kwargs)
        return decorated_function
    return decorator

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

class SessionManager:
    def __init__(self):
        self.redis = redis_client
        self.session_duration = 24 * 60 * 60  # 24 hours

    def create_session(self, user_id: int, device_info: dict) -> str:
        """Create new session with device tracking"""
        session_id = generate_session_id()
        session_data = {
            'user_id': user_id,
            'device_info': device_info,
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat()
        }
        
        self.redis.setex(
            f"session:{session_id}",
            self.session_duration,
            json.dumps(session_data)
        )
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """Validate session and update last active time"""
        session_key = f"session:{session_id}"
        if self.redis.exists(session_key):
            session_data = json.loads(self.redis.get(session_key))
            session_data['last_active'] = datetime.utcnow().isoformat()
            self.redis.setex(session_key, self.session_duration, json.dumps(session_data))
            return True
        return False
