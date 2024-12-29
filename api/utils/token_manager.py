import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import jwt
from utils.db_utils import get_db_connection
from models.users import Users  # Assuming the Users model is defined in models/users.py
from datetime import datetime, timedelta
from typing import Dict, Any

class TokenManager:
    def __init__(self):
        self.db = get_db_connection()
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        self.token_storage = TokenStorage()

    def generate_access_token(self, user: Users) -> str:
        """Generate access token for user"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def generate_refresh_token(self, user: Users) -> str:
        """Generate refresh token for user"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    # Additional methods for token management can be added here

...rest of the code...
