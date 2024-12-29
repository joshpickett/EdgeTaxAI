from cryptography.fernet import Fernet
import base64
import os
from typing import Optional

class EncryptionManager:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.key)

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
