import os
import sys
from api.setup_path import setup_python_path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from models.users import Users
from api.utils.encryption_utils import EncryptionManager

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

class TokenManager:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        self.encryption_manager = EncryptionManager()
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=7)
        self.refresh_threshold = timedelta(minutes=5)

    def generate_access_token(self, user: Users) -> str:
        """Generate access token for user"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + self.access_token_expire,
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        encrypted_token = self.encryption_manager.encrypt(token)
        return encrypted_token

    def generate_refresh_token(self, user: Users) -> str:
        """Generate refresh token for user"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + self.refresh_token_expire,
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        encrypted_token = self.encryption_manager.encrypt(token)
        return encrypted_token

    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            decrypted_token = self.encryption_manager.decrypt(token)
            if not decrypted_token:
                return None
            claims = jwt.decode(decrypted_token, self.secret_key, algorithms=['HS256'])
            return claims
        except jwt.InvalidTokenError:
            return None

    # Additional methods for token management can be added here

...rest of the code...
