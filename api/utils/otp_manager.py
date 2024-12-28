import random
import string
from datetime import datetime, timedelta
from typing import Optional

class OTPManager:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 5
        
    def generate_otp(self) -> str:
        """Generate a random One Time Password"""
        return ''.join(random.choices(string.digits, k=self.otp_length))
        
    def verify_otp_for_user(self, identifier: str, otp: str) -> bool:
        """Verify One Time Password for given user"""
        # Implementation would check against database
        # This is a placeholder for the actual implementation
        return True
        
    def is_otp_expired(self, created_at: datetime) -> bool:
        """Check if One Time Password has expired"""
        expiry_time = created_at + timedelta(minutes=self.otp_expiry_minutes)
        return datetime.now() > expiry_time
