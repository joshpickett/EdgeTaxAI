import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

class TokenStorage:
    def __init__(self, secret_key: str):
        self.fernet = Fernet(secret_key.encode())
        self.storage_path = os.path.join(os.path.expanduser('~'), '.taxedgeai', 'tokens')
        os.makedirs(self.storage_path, exist_ok=True)
        
    def store_token(self, user_id: int, platform: str, token_data: Dict[str, Any]) -> bool:
        """Securely store platform tokens"""
        try:
            filename = self._get_token_file(user_id, platform)
            encrypted_data = self.fernet.encrypt(json.dumps(token_data).encode())
            
            with open(filename, 'wb') as file:
                file.write(encrypted_data)
            return True
        except Exception as exception:
            logging.error(f"Error storing token: {exception}")
            return False
            
    def get_token(self, user_id: int, platform: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored token data"""
        try:
            filename = self._get_token_file(user_id, platform)
            if not os.path.exists(filename):
                return None
                
            with open(filename, 'rb') as file:
                encrypted_data = file.read()
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as exception:
            logging.error(f"Error retrieving token: {exception}")
            return None
            
    def delete_token(self, user_id: int, platform: str) -> bool:
        """Delete stored token data"""
        try:
            filename = self._get_token_file(user_id, platform)
            if os.path.exists(filename):
                os.remove(filename)
            return True
        except Exception as exception:
            logging.error(f"Error deleting token: {exception}")
            return False
            
    def _get_token_file(self, user_id: int, platform: str) -> str:
        """Get token file path"""
        return os.path.join(self.storage_path, f"{user_id}_{platform}_token.enc")
