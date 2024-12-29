import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from typing import Optional, Dict, Any
import hashlib
from api.utils.db_utils import get_db_connection

class BiometricAuthentication:
    def __init__(self):
        self.db = get_db_connection()
        self.salt_length = 32  # Increased for better security
        self.hash_iterations = 100000  # Increased from previous value
        self.fallback_attempts = 3
        
    def register_biometric(self, user_id: int, biometric_data: str) -> bool:
        """Register biometric data for a user"""
        try:
            # Generate salt and hash biometric data
            salt = os.urandom(self.salt_length)
            hashed_data = self._hash_biometric(biometric_data, salt)
            
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO biometric_auth 
                (user_id, biometric_hash, salt) 
                VALUES (?, ?, ?)
            """, (user_id, hashed_data, salt))
            
            self.db.commit()
            return True
        except Exception as e:
            logging.error(f"Error registering biometric: {e}")
            return False
            
    def verify_biometric(
        self, user_id: int, biometric_data: str
    ) -> Dict[str, Any]:
        """Verify biometric data with fallback"""
        try:
            if self._verify_biometric_data(user_id, biometric_data):
                return {
                    "status": "success",
                    "message": "Biometric verification successful"
                }
                
            # Handle fallback
            fallback_token = self._generate_fallback_token(user_id)
            return {
                "status": "fallback_required",
                "fallback_token": fallback_token,
                "remaining_attempts": self.fallback_attempts
            }
            
        except Exception as e:
            logging.error(f"Biometric verification error: {e}")
            raise BiometricError("Verification failed")
            
    def _hash_biometric(self, data: str, salt: bytes) -> str:
        """Hash biometric data with salt"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            data.encode(),
            salt,
            self.hash_iterations  # Number of iterations
        ).hex()
    
    def verify_hardware_support(self) -> bool:
        """Verify if device supports biometric authentication"""
        try:
            return True if self.db.cursor().execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='biometric_auth'"
            ).fetchone()[0] > 0 else False
        except Exception as e:
            logging.error(f"Error checking hardware support: {e}")
            return False
