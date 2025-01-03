# api/utils/otp_manager.py

import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio
from .encryption_utils import EncryptionManager
from .session_manager import SessionManager
from .audit_trail import AuditLogger

class OTPManager:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 5
        self.max_retries = 3
        self.retry_delay = 30  # seconds
        self.encryption_manager = EncryptionManager()
        self.session_manager = SessionManager()
        self.audit_logger = AuditLogger()

    async def generate_and_send_otp(self, identifier: str) -> Dict[str, Any]:
        """Generate and send an encrypted OTP"""
        try:
            # Generate OTP
            otp = "".join(random.choices(string.digits, k=self.otp_length))
            
            # Encrypt OTP before storage
            encrypted_otp = self.encryption_manager.encrypt(otp)
            
            # Create temporary session for OTP verification
            session_id = self.session_manager.create_session(
                identifier,
                {
                    "purpose": "otp_verification",
                    "encrypted_otp": encrypted_otp,
                    "attempts": 0,
                    "expires_at": (datetime.now() + timedelta(minutes=self.otp_expiry_minutes)).isoformat()
                }
            )

            for attempt in range(self.max_retries):
                try:
                    if "@" in identifier:
                        success = await self._send_email_otp(identifier, otp)
                    else:
                        success = await self._send_sms_otp(identifier, otp)

                    if success:
                        self.audit_logger.log_event(
                            "otp_sent",
                            {"identifier": identifier, "session_id": session_id}
                        )
                        return {
                            "status": "success",
                            "message": "OTP sent successfully",
                            "session_id": session_id
                        }

                    await asyncio.sleep(self.retry_delay)

                except Exception as e:
                    self.audit_logger.log_error(
                        "otp_send_failed",
                        {"identifier": identifier, "attempt": attempt + 1, "error": str(e)}
                    )
                    if attempt == self.max_retries - 1:
                        raise OTPError(f"Failed to send OTP after {self.max_retries} attempts")
                    continue

        except Exception as e:
            self.audit_logger.log_error(
                "otp_generation_failed",
                {"identifier": identifier, "error": str(e)}
            )
            raise

    async def verify_otp(self, session_id: str, provided_otp: str) -> bool:
        """Verify OTP with encryption and session management"""
        try:
            # Get session data
            session_data = self.session_manager.get_session(session_id)
            if not session_data:
                return False

            # Check expiration
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.now() > expires_at:
                self.session_manager.invalidate_session(session_id)
                return False

            # Increment attempt counter
            session_data["attempts"] += 1
            if session_data["attempts"] >= 3:
                self.session_manager.invalidate_session(session_id)
                return False

            # Decrypt stored OTP and compare
            stored_otp = self.encryption_manager.decrypt(session_data["encrypted_otp"])
            if stored_otp == provided_otp:
                self.session_manager.invalidate_session(session_id)
                self.audit_logger.log_event(
                    "otp_verified",
                    {"session_id": session_id}
                )
                return True

            self.session_manager.update_session(session_id, session_data)
            return False

        except Exception as e:
            self.audit_logger.log_error(
                "otp_verification_failed",
                {"session_id": session_id, "error": str(e)}
            )
            return False

    async def _send_email_otp(self, email: str, otp: str) -> bool:
        """Send OTP via email"""
        # Implementation of email sending logic
        pass

    async def _send_sms_otp(self, phone: str, otp: str) -> bool:
        """Send OTP via SMS"""
        # Implementation of SMS sending logic
        pass

class OTPError(Exception):
    """Custom exception for OTP-related errors"""
    pass