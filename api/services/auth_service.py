import os
import sys
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from api.models.users import Users, UserRole
from api.utils.encryption_utils import EncryptionManager
from api.utils.validators import validate_login_input
from api.utils.token_manager import TokenManager
from api.utils.session_manager import SessionManager
from api.utils.biometric_auth import BiometricAuthentication
from api.exceptions.auth_exceptions import AuthenticationError, APIError
from api.utils.audit_trail import AuditLogger
from api.utils.device_fingerprint import DeviceFingerprint
from api.utils.otp_service import generate_otp, send_otp

# Set up path for both package and direct execution
setup_python_path()

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple
from api.config.database import SessionLocal

session_manager = SessionManager()
encryption_manager = EncryptionManager()


class AuthService:
    def __init__(self):
        self.token_manager = TokenManager()
        self.db = SessionLocal()
        self.biometric_auth = BiometricAuthentication()
        self.audit_logger = AuditLogger()
        self.device_fingerprint = DeviceFingerprint()
        self.max_login_attempts = 5
        self.lockout_duration = 30  # minutes

    def handle_signup(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        try:
            identifier = data.get("email") or data.get("phone_number")
            self.audit_logger.log_auth_attempt(identifier, "signup_attempt")

            if self.user_exists(identifier):
                self.audit_logger.log_auth_failure(identifier, "user_exists")
                raise AuthenticationError("User already exists")

            # Generate and save OTP
            otp = generate_otp()
            expiry = datetime.now(timezone.utc) + timedelta(minutes=5)

            # Create new user with OTP
            new_user = Users(
                email=identifier if "@" in identifier else None,
                phone_number=identifier if "@" not in identifier else None,
                otp_code=otp,
                otp_expiry=expiry,
                role=UserRole.User,
            )
            self.db.add(new_user)
            self.db.commit()

            # Send OTP
            if not send_otp(identifier, otp):
                raise AuthenticationError("Failed to send OTP")

            return {"message": "OTP sent"}, 200

        except Exception as e:
            logging.error(f"Signup error: {str(e)}")
            raise

    def user_exists(self, identifier: str) -> bool:
        """Check if user exists by email or phone"""
        try:
            user = (
                self.db.query(Users)
                .filter(
                    (Users.email == identifier) | (Users.phone_number == identifier)
                )
                .first()
            )
            return user is not None
        except Exception as e:
            logging.error(f"Error checking user existence: {str(e)}")
            raise

    def verify_otp(self, data: Dict[str, Any]) -> bool:
        """Verify OTP code"""
        identifier = data.get("email") or data.get("phone_number")
        otp_code = data.get("otp_code")

        try:
            user = (
                self.db.query(Users)
                .filter(
                    ((Users.email == identifier) | (Users.phone_number == identifier))
                    & (Users.otp_code == otp_code)
                )
                .first()
            )

            if not user:
                return False

            expiry = user.otp_expiry
            return datetime.now(timezone.utc) <= expiry

        except Exception as e:
            logging.error(f"Error verifying OTP: {str(e)}")
            return False

    def handle_biometric_registration(self, user_id: int, biometric_data: str) -> bool:
        """Register biometric data for a user"""
        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()
            if not user:
                raise AuthenticationError("User not found")

            # Store biometric data securely
            success = self.biometric_auth.register_biometric(user_id, biometric_data)
            if success:
                user.biometric_data = (
                    "registered"  # Flag as registered without storing actual data
                )
                self.db.commit()
                return True
            return False
        except Exception as e:
            logging.error(f"Biometric registration error: {str(e)}")
            raise AuthenticationError("Failed to register biometric data")

    def verify_biometric(self, user_id: int, biometric_data: str) -> Dict[str, Any]:
        """Verify biometric data"""
        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()
            if not user or not user.biometric_data:
                return {"status": "failure", "message": "Biometric data not found"}
            if self.biometric_auth.verify_biometric_data(user_id, biometric_data):
                return {
                    "status": "success",
                    "message": "Biometric verification successful",
                }
            else:
                fallback_token = self.biometric_auth.generate_fallback_token(user_id)
                return {
                    "status": "fallback_required",
                    "fallback_token": fallback_token,
                    "remaining_attempts": self.biometric_auth.fallback_attempts,
                }
        except Exception as e:
            logging.error(f"Biometric verification error: {str(e)}")
            return {"status": "error", "message": "Verification failed"}

    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()
            if user:
                user.last_login = datetime.now(timezone.utc)
                self.db.commit()
        except Exception as e:
            logging.error(f"Error updating last login: {str(e)}")

    async def handle_login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            validate_login_input(data)
            
            identifier = data.get("email") or data.get("phone_number")
            device_info = data.get("device_info", {})

            # Enhanced security checks
            await encryption_manager.rotate_key_if_needed()
            if self.is_account_locked(identifier):
                raise AuthenticationError(
                    "Account temporarily locked. Please try again later."
                )

            # Generate device fingerprint
            device_fingerprint = self.device_fingerprint.generate_fingerprint()

            user = self.get_user_by_identifier(identifier)

            if not user:
                return {"error": "User not found"}

            # Handle remembered devices
            if device_info.get("remember_device", False):
                device_token = self.register_trusted_device(user.id, device_fingerprint)

            # Additional login logic here...

        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            raise AuthenticationError("Login failed")

    def register_trusted_device(self, user_id: int, device_fingerprint: str) -> str:
        """Register a trusted device"""
        try:
            device_token = generate_device_token()
            self.db.execute(
                """INSERT INTO trusted_devices 
                   (user_id, device_fingerprint, device_token)
                   VALUES (?, ?, ?)""",
                (user_id, device_fingerprint, device_token),
            )
            return device_token
        except Exception as e:
            logging.error(f"Error registering trusted device: {str(e)}")
            raise
