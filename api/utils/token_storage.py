from typing import Optional, Dict
from datetime import datetime, timedelta


class TokenStorage:
    def __init__(self):
        self._tokens: Dict[str, Dict] = {}

    def store_token(self, user_id: str, token: str, expires_in: int = 3600) -> None:
        """Store a token with expiration"""
        self._tokens[user_id] = {
            "token": token,
            "expires_at": datetime.now() + timedelta(seconds=expires_in),
        }

    def get_token(self, user_id: str) -> Optional[str]:
        """Retrieve a valid token"""
        token_data = self._tokens.get(user_id)
        if not token_data:
            return None

        if datetime.now() > token_data["expires_at"]:
            del self._tokens[user_id]
            return None

        return token_data["token"]

    def invalidate_token(self, user_id: str) -> None:
        """Invalidate a user's token"""
        if user_id in self._tokens:
            del self._tokens[user_id]
