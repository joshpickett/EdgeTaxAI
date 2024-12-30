from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

class EncryptionManager:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.key)
        self.key_rotation_interval = timedelta(days=30)
        self.last_rotation = datetime.now()
        self.logger = logging.getLogger(__name__)

    def should_rotate_key(self) -> bool:
        """Check if key rotation is needed"""
        return datetime.now() - self.last_rotation >= self.key_rotation_interval

    async def rotate_key_if_needed(self) -> None:
        """Automatically rotate key if needed"""
        if self.should_rotate_key():
            try:
                await self.rotate_key()
            except Exception as e:
                self.logger.error(f"Key rotation failed: {str(e)}")

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return None
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return None

    def rotate_key(self) -> None:
        """Rotate encryption key"""
        new_key = Fernet.generate_key()
        self.key = new_key
        self.cipher_suite = Fernet(new_key)
