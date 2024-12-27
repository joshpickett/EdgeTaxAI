import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging
from flask import request, jsonify, current_app
import redis
import os

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def rate_limit(requests_per_minute: int = 30):
    """
    Rate limiting decorator that restricts the number of requests per minute per IP
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            key = f"rate_limit:{ip}"
             
            # Get current count
            count = redis_client.get(key)
            if count is None:
                redis_client.setex(key, 60, 1)  # expire in 60 seconds
            else:
                count = int(count)
                if count >= requests_per_minute:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                redis_client.incr(key)
             
            return f(*args, **kwargs)
        return wrapper
    return decorator

def check_login_attempts(identifier: str) -> bool:
    """
    Check if user has exceeded maximum login attempts
    Returns True if allowed to proceed, False if too many attempts
    """
    key = f"login_attempts:{identifier}"
     
    # Get current attempts
    attempts = redis_client.get(key)
     
    if attempts is None:
        redis_client.setex(key, 3600, 1)  # expire in 1 hour
        return True
    
    attempts = int(attempts)
    if attempts >= 5:
        return False
    
    redis_client.incr(key)
    return True

def reset_login_attempts(identifier: str) -> None:
    """Reset login attempts for a user after successful login"""
    key = f"login_attempts:{identifier}"
    redis_client.delete(key)
