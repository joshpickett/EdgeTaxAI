from functools import wraps
from flask import request, jsonify
from typing import Callable, Any
import jwt
from datetime import datetime, timedelta
import os

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

def rate_limit(requests_per_minute: int) -> Callable:
    """Rate limiting decorator"""
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Implement rate limiting logic here
            return function(*args, **kwargs)
        return decorated_function
    return decorator
