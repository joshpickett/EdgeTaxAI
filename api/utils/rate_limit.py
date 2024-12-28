from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
from collections import defaultdict

# Store login attempts in memory (could be moved to Redis/database for production)
login_attempts = defaultdict(list)

def check_login_attempts(ip_address):
    """Check if IP has exceeded login attempts"""
    now = datetime.now()
    # Clean old attempts
    login_attempts[ip_address] = [
        attempt for attempt in login_attempts[ip_address]
        if now - attempt < timedelta(minutes=15)
    ]
    # Check if too many attempts
    if len(login_attempts[ip_address]) >= 5:
        return False
    login_attempts[ip_address].append(now)
    return True

def rate_limit(requests_per_minute):
    def decorator(f):
        requests = defaultdict(list)
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            ip = request.remote_addr
            
            # Clean old requests
            requests[ip] = [req for req in requests[ip] 
                          if now - req < timedelta(minutes=1)]
            
            if len(requests[ip]) >= requests_per_minute:
                return jsonify({"error": "Rate limit exceeded"}), 429
                
            requests[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator
