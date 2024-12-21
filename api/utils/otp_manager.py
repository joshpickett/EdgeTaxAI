import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from .db_utils import get_db_connection

class OTPManager:
    def __init__(self):
        self.db = get_db_connection()
        self.otp_length = 6
        self.otp_expiry = 5  # minutes
        
    def generate_otp(self) -> str:
        """Generate a random One-Time Password of specified length"""
        return ''.join([str(random.randint(0, 9)) for _ in range(self.otp_length)])
        
    def save_otp(self, user_id: int, otp: str) -> bool:
        """Save One-Time Password with expiry time"""
        try:
            expiry = datetime.now() + timedelta(minutes=self.otp_expiry)
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE users 
                SET otp_code = ?, otp_expiry = ? 
                WHERE id = ?
            """, (otp, expiry.isoformat(), user_id))
            self.db.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving One-Time Password: {e}")
            return False
            
    def verify_otp(self, user_id: int, otp: str) -> Tuple[bool, Optional[str]]:
        """Verify One-Time Password and return status with optional error message"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT otp_code, otp_expiry 
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, "User not found"
                
            stored_otp, expiry = row
            expiry_time = datetime.fromisoformat(expiry)
            
            if datetime.now() > expiry_time:
                return False, "One-Time Password expired"
                
            if otp != stored_otp:
                return False, "Invalid One-Time Password"
                
            return True, None
            
        except Exception as e:
            logging.error(f"Error verifying One-Time Password: {e}")
            return False, "Verification failed"
