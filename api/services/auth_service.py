import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple
from api.services.db_service import DatabaseService
from api.utils.session_manager import SessionManager
from api.utils.token_manager import TokenManager
from api.utils.otp_service import generate_otp, send_otp
from api.exceptions.auth_exceptions import AuthenticationError

session_manager = SessionManager()

class AuthService:
    def __init__(self):
        self.db = DatabaseService()
        self.token_manager = TokenManager()
        
    def handle_signup(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        try:
            identifier = data.get("email") or data.get("phone_number")
            if not identifier:
                raise AuthenticationError("Email or phone number required")
                
            # Validate identifier
            if "@" in identifier:
                if not validate_email(identifier):
                    raise AuthenticationError("Invalid email format")
            else:
                if not validate_phone(identifier):
                    raise AuthenticationError("Invalid phone format")
                    
            # Generate and save OTP
            otp = generate_otp()
            expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
            
            # Create session for the signup process
            session_manager.create_session(identifier, {'signup_stage': 'otp_sent'})
 
            self.db.execute_query(
                """INSERT INTO users (email, phone_number, otp_code, otp_expiry) 
                   VALUES (?, ?, ?, ?)""",
                (identifier if "@" in identifier else None,
                 identifier if "@" not in identifier else None,
                 otp, expiry)
            )
            
            # Send OTP
            send_otp(identifier, otp)
            
            return {"message": "OTP sent"}, 200
            
        except Exception as e:
            logging.error(f"Signup error: {str(e)}")
            raise
            
    def user_exists(self, identifier: str) -> bool:
        """Check if user exists by email or phone"""
        try:
            result = self.db.execute_query(
                """SELECT id FROM users 
                   WHERE email = ? OR phone_number = ?""",
                (identifier, identifier),
                fetch_one=True
            )
            return bool(result)
        except Exception as e:
            logging.error(f"Error checking user existence: {str(e)}")
            raise
            
    def verify_otp(self, data: Dict[str, Any]) -> bool:
        """Verify OTP code"""
        identifier = data.get("email") or data.get("phone_number")
        otp_code = data.get("otp_code")
        
        result = self.db.execute_query(
            """SELECT otp_code, otp_expiry FROM users 
               WHERE (email = ? OR phone_number = ?) AND otp_code = ?""",
            (identifier, identifier, otp_code),
            fetch_one=True
        )
        
        if not result:
            return False
            
        expiry = datetime.fromisoformat(result[1])
        return datetime.now(timezone.utc) <= expiry
        
    def handle_biometric_registration(self, user_id: int, biometric_data: str) -> bool:
        """Handle biometric registration"""
        try:
            self.db.execute_query(
                "UPDATE users SET biometric_data = ? WHERE id = ?",
                (biometric_data, user_id)
            )
            return True
        except Exception as e:
            logging.error(f"Biometric registration error: {str(e)}")
            return False
