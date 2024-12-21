import redis
import json
import logging
from typing import Optional, Any, Dict
from functools import wraps
from datetime import timedelta

# Configure Redis client
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Configure logging
logging.basicConfig(
    filename='cache.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CacheManager:
    def __init__(self, default_timeout: int = 3600):
        self.default_timeout = default_timeout

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logging.error(f"Cache get error: {str(e)}")
            return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Store value in cache."""
        try:
            timeout = timeout or self.default_timeout
            return redis_client.setex(
                key,
                timeout,
                json.dumps(value)
            )
        except Exception as e:
            logging.error(f"Cache set error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Remove value from cache."""
        try:
            return redis_client.delete(key) > 0
        except Exception as e:
            logging.error(f"Cache delete error: {str(e)}")
            return False

def cache_response(timeout: int = 3600):
    """Decorator for caching API responses."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache first
            cache_manager = CacheManager()
            cached_response = cache_manager.get(cache_key)
            
            if cached_response is not None:
                logging.info(f"Cache hit for key: {cache_key}")
                return cached_response
            
            # If not in cache, execute function
            response = f(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, response, timeout)
            logging.info(f"Cached response for key: {cache_key}")
            
            return response
        return wrapper
    return decorator
