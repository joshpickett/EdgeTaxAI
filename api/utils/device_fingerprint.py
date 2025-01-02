import hashlib
from flask import request
from typing import Dict, Any


class DeviceFingerprint:
    def __init__(self):
        self.fingerprint_version = "1.0"

    def generate_fingerprint(self) -> str:
        """Generate a unique device fingerprint based on request headers"""
        device_data = {
            "user_agent": request.headers.get("User-Agent", ""),
            "accept_language": request.headers.get("Accept-Language", ""),
            "platform": request.headers.get("Sec-Ch-Ua-Platform", ""),
            "mobile": request.headers.get("Sec-Ch-Ua-Mobile", ""),
            "ip": request.remote_addr,
            "version": self.fingerprint_version,
        }

        fingerprint_string = "|".join(str(v) for v in device_data.values())
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    def validate_fingerprint(self, stored_fingerprint: str) -> bool:
        """Validate current device fingerprint against stored one"""
        current_fingerprint = self.generate_fingerprint()
        return stored_fingerprint == current_fingerprint
