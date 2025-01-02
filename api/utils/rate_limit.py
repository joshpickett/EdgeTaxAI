from datetime import datetime, timedelta
from typing import Dict, Any
import redis
from api.utils.error_handler import RateLimitError


class RateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True,
        )
        self.default_limit = 100
        self.default_window = 3600

    def check_rate(
        self, key: str, max_requests: int = None, window_seconds: int = None
    ) -> bool:
        """Check if the rate limit has been exceeded"""
        try:
            max_requests = max_requests or self.default_limit
            window_seconds = window_seconds or self.default_window

            current = self.redis_client.get(key)
            if current is None:
                self.redis_client.setex(key, window_seconds, 1)
                return True

            count = int(current)
            if count >= max_requests:
                ttl = self.redis_client.ttl(key)
                raise RateLimitError(
                    message="Rate limit exceeded",
                    limit=max_requests,
                    window=window_seconds,
                )

            self.redis_client.incr(key)

            # Add rate limit headers
            remaining = max_requests - count - 1
            reset_time = int(datetime.now().timestamp()) + ttl

            return {"remaining": remaining, "reset": reset_time}

        except Exception as exception:
            # If Redis is unavailable, default to allowing the request
            return True

    def reset_rate(self, key: str) -> None:
        """Reset rate limit counter for a key"""
        try:
            self.redis_client.delete(key)
        except Exception:
            pass
