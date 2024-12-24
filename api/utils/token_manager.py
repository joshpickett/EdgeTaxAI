import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Dict

class TokenManager:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)
        self.refresh_threshold = 300  # 5 minutes before expiry

    def check_token_expiry(self, user_id: int, platform: str) -> bool:
        """Check if token needs refresh"""
        try:
            key = f"tokens:{user_id}:{platform}"
            token_data = self.redis.get(key)
            if not token_data:
                return True

            token_info = json.loads(token_data)
            expiry = datetime.fromisoformat(token_info.get('expires_at', ''))
            
            # Check if token expires in next 5 minutes
            return (expiry - datetime.now()).total_seconds() < self.refresh_threshold
        except Exception as e:
            logging.error(f"Token expiry check error: {e}")
            return True

    def refresh_token(self, user_id: int, platform: str, new_tokens: Dict[str, str]) -> bool:
        """Update tokens after refresh"""
        try:
            key = f"tokens:{user_id}:{platform}"
            new_tokens['refreshed_at'] = datetime.now().isoformat()
            
            # Calculate token expiry
            expires_in = new_tokens.get('expires_in', 3600)  # Default 1 hour
            new_tokens['expires_at'] = (
                datetime.now() + timedelta(seconds=expires_in)
            ).isoformat()
            
            self.redis.setex(
                key,
                timedelta(seconds=expires_in),
                json.dumps(new_tokens)
            )
            return True
        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            return False

    def verify_token(self, token: str) -> Dict[str, str]:
        """Verify the provided token and return claims"""
        # Implementation for verifying the token
        pass

    def can_refresh(self, token: str) -> bool:
        """Check if the token can be refreshed"""
        # Implementation for checking if the token can be refreshed
        pass
