from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from api.config.security_config import SECURITY_CONFIG

class TaxDataEncryption:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.key = self._generate_key()
        self.cipher_suite = Fernet(self.key)
        self.sensitive_fields = SECURITY_CONFIG['AUDIT']['SENSITIVE_FIELDS']

    def _generate_key(self) -> bytes:
        """Generate encryption key using PBKDF2"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(
            os.getenv('TAX_ENCRYPTION_SECRET').encode()
        ))
        return key

    def encrypt_tax_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive tax data fields"""
        encrypted_data = data.copy()
        
        for field in self.sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self._encrypt_value(str(encrypted_data[field]))
                
        return encrypted_data

    def decrypt_tax_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive tax data fields"""
        decrypted_data = data.copy()
        
        for field in self.sensitive_fields:
            if field in decrypted_data:
                decrypted_data[field] = self._decrypt_value(str(decrypted_data[field]))
                
        return decrypted_data

    def _encrypt_value(self, value: str) -> str:
        """Encrypt individual value"""
        try:
            return self.cipher_suite.encrypt(value.encode()).decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            raise

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt individual value"""
        try:
            return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            raise

    def rotate_key(self) -> None:
        """Rotate encryption key"""
        new_key = self._generate_key()
        old_cipher_suite = self.cipher_suite
        self.cipher_suite = Fernet(new_key)
        self.key = new_key
        return old_cipher_suite
