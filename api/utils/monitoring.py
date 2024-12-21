import time
import logging
from functools import wraps
from typing import Callable, Any
import redis

# Configure Redis client for monitoring
redis_client = redis.Redis(host='localhost', port=6379, db=1)

def monitor_api_calls(endpoint: str) -> Callable:
    """
    Decorator to monitor API calls and track metrics.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Increment API call counter
            try:
                redis_client.incr(f"api_calls:{endpoint}")
                redis_client.expire(f"api_calls:{endpoint}", 86400)  # Expire after 24 hours
            except Exception as e:
                logging.error(f"Redis increment error: {e}")

            try:
                result = f(*args, **kwargs)
                
                # Record response time
                response_time = time.time() - start_time
                try:
                    redis_client.lpush(f"response_times:{endpoint}", response_time)
                    redis_client.ltrim(f"response_times:{endpoint}", 0, 999)  # Keep last 1000 times
                except Exception as e:
                    logging.error(f"Redis timing error: {e}")

                return result
            except Exception as e:
                # Track errors
                try:
                    redis_client.incr(f"errors:{endpoint}")
                    redis_client.expire(f"errors:{endpoint}", 86400)
                except Exception as redis_error:
                    logging.error(f"Redis error tracking failed: {redis_error}")
                raise e
            
        return wrapper
    return decorator

def get_api_metrics(endpoint: str) -> dict:
    """
    Get API metrics for a specific endpoint.
    """
    try:
        calls = int(redis_client.get(f"api_calls:{endpoint}") or 0)
        errors = int(redis_client.get(f"errors:{endpoint}") or 0)
        
        # Calculate average response time
        times = redis_client.lrange(f"response_times:{endpoint}", 0, -1)
        avg_time = sum(float(t) for t in times) / len(times) if times else 0
        
        return {
            "total_calls": calls,
            "error_count": errors,
            "error_rate": (errors / calls * 100) if calls > 0 else 0,
            "avg_response_time": avg_time
        }
    except Exception as e:
        logging.error(f"Error fetching metrics: {e}")
        return {}

def clear_metrics(endpoint: str = None) -> None:
    """
    Clear metrics for a specific endpoint or all endpoints.
    """
    try:
        if endpoint:
            redis_client.delete(f"api_calls:{endpoint}")
            redis_client.delete(f"errors:{endpoint}")
            redis_client.delete(f"response_times:{endpoint}")
        else:
            for key in redis_client.keys("api_calls:*"):
                redis_client.delete(key)
            for key in redis_client.keys("errors:*"):
                redis_client.delete(key)
            for key in redis_client.keys("response_times:*"):
                redis_client.delete(key)
    except Exception as e:
        logging.error(f"Error clearing metrics: {e}")
