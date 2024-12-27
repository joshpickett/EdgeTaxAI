import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional
from utils.otp_manager import OTPManager
from utils.token_storage import TokenStorage
from utils.biometric_auth import BiometricAuthentication
from utils.db_utils import get_db_connection
from datetime import datetime, timedelta, timezone
import logging

class AuthService:
    def __init__(self):
        self.db = get_db_connection()
        self.otp_manager = OTPManager()
        self.token_storage = TokenStorage()
        self.biometric_auth = BiometricAuthentication()
        
    def handle_signup(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
        """Handle user signup process"""
        try:
            email = data.get("email")
            phone_number = data.get("phone_number")
            
            if not (email or phone_number):
                return {"error": "Email or phone number is required."}, 400
                
            # Check if user exists
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ? OR phone_number = ?",
                (email, phone_number)
            )
            if cursor.fetchone():
                return {"error": "User already exists."}, 400
                
            # Create new user
            cursor.execute(
                "INSERT INTO users (email, phone_number, is_verified) VALUES (?, ?, 0)",
                (email, phone_number)
            )
            self.db.commit()
            
            # Generate and send OTP
            identifier = email or phone_number
            otp = self.otp_manager.generate_otp()
            self.otp_manager.save_otp(identifier, otp)
            
            return {"message": "Signup successful. OTP sent for verification."}, 201
            
        except Exception as e:
            logging.error(f"Signup error: {e}")
            return {"error": str(e)}, 500
            
    def handle_login(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
        """Handle user login process"""
        try:
            identifier = data.get("email") or data.get("phone_number")
            
            if not identifier:
                return {"error": "Email or phone number required."}, 400
                
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ? OR phone_number = ?",
                (identifier, identifier)
            )
            user = cursor.fetchone()
            
            if not user:
                return {"error": "User not found."}, 404
                
            # Generate and send OTP
            otp = self.otp_manager.generate_otp()
            self.otp_manager.save_otp(identifier, otp)
            
            return {"message": "OTP sent for verification."}, 200
            
        except Exception as e:
            logging.error(f"Login error: {e}")
            return {"error": str(e)}, 500
            
    def verify_otp(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
        """Verify OTP for user authentication"""
        try:
            identifier = data.get("email") or data.get("phone_number")
            otp_code = data.get("otp_code")
            
            if not all([identifier, otp_code]):
                return {"error": "Missing required fields."}, 400
                
            if self.otp_manager.verify_otp(identifier, otp_code):
                cursor = self.db.cursor()
                cursor.execute(
                    "UPDATE users SET is_verified = 1 WHERE email = ? OR phone_number = ?",
                    (identifier, identifier)
                )
                self.db.commit()
                return {"message": "OTP verified successfully."}, 200
                
            return {"error": "Invalid or expired OTP."}, 401
            
        except Exception as e:
            logging.error(f"OTP verification error: {e}")
            return {"error": str(e)}, 500
            
    def handle_biometric_registration(self, user_id: int, biometric_data: str) -> tuple[Dict[str, Any], int]:
        """Handle biometric registration"""
        try:
            if not all([user_id, biometric_data]):
                return {"error": "Missing required data."}, 400
                
            success = self.biometric_auth.register_biometric(user_id, biometric_data)
            
            if success:
                return {"message": "Biometric registration successful."}, 200
            return {"error": "Biometric registration failed."}, 400
            
        except Exception as e:
            logging.error(f"Biometric registration error: {e}")
            return {"error": str(e)}, 500
