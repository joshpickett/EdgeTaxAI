import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import keyring
import platform

class TokenStorage:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.token_expiry = 24  # hours
        self.refresh_token_expiry = 7 * 24  # 7 days
        self.token_type = 'Bearer'
        
    def _get_storage_key(self, user_id: int, token_type: str = 'access') -> str:
        """Generate storage key for tokens"""
        return f'user_{user_id}_{token_type}_token'

    def generate_token(self, user_id: int, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JSON Web Token with claims"""
        try:
            claims = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry),
                'iat': datetime.utcnow()
            }
            
            if additional_claims:
                claims.update(additional_claims)
                
            return jwt.encode(claims, self.secret_key, algorithm='HS256')
        except Exception as e:
            logging.error(f"Error generating token: {e}")
            raise
            
    def store_token(self, user_id: int, token: str) -> bool:
        """Store token securely based on platform"""
        try:
            storage_key = self._get_storage_key(user_id)
            keyring.set_password('taxedgeai', storage_key, token)
            
            # Store refresh token if provided
            if 'refresh_token' in token:
                refresh_key = self._get_storage_key(user_id, 'refresh')
                keyring.set_password('taxedgeai', refresh_key, token['refresh_token'])
                
            return True
        except Exception as e:
            logging.error(f"Error storing token: {e}")
            return False
            
    def retrieve_token(self, user_id: int) -> Optional[str]:
        """Retrieve stored token"""
        try:
            return keyring.get_password('taxedgeai', self._get_storage_key(user_id))
        except Exception as e:
            logging.error(f"Error retrieving token: {e}")
            return None
            
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify token and return claims if valid"""
        try:
            claims = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return True, claims
        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return False, {'error': 'Invalid token'}
        except Exception as e:
            logging.error(f"Error verifying token: {e}")
            return False, {'error': str(e)}
