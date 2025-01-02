import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio


class OTPError(Exception):
    pass


class OTPManager:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 5
        self.max_retries = 3
        self.retry_delay = 30  # seconds

    async def generate_and_send_otp(self, identifier: str) -> Dict[str, Any]:
        """Generate a random One Time Password"""
        otp = "".join(random.choices(string.digits, k=self.otp_length))

        for attempt in range(self.max_retries):
            try:
                if "@" in identifier:
                    success = await self._send_email_otp(identifier, otp)
                else:
                    success = await self._send_sms_otp(identifier, otp)

                if success:
                    return {"status": "success", "message": "OTP sent successfully"}

                await asyncio.sleep(self.retry_delay)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise OTPError(
                        f"Failed to send OTP after {self.max_retries} attempts"
                    )
                continue

    def verify_otp_for_user(self, identifier: str, otp: str) -> bool:
        """Verify One Time Password for given user"""
        # Implementation would check against database
        # This is a placeholder for the actual implementation
        return True

    def is_otp_expired(self, created_at: datetime) -> bool:
        """Check if One Time Password has expired"""
        expiry_time = created_at + timedelta(minutes=self.otp_expiry_minutes)
        return datetime.now() > expiry_time
