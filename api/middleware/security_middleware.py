from typing import Dict, Any
from functools import wraps
from flask import request, jsonify
from api.config.security_config import SECURITY_CONFIG
from api.utils.encryption_utils import EncryptionManager
from api.utils.audit_logger import AuditLogger
from api.utils.rate_limit import RateLimiter
import ipaddress
import logging


class SecurityMiddleware:
    def __init__(self, db):
        self.encryption_manager = EncryptionManager()
        self.audit_logger = AuditLogger(db)
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(__name__)
        self.allowed_ips = self._load_allowed_ips()

    def _load_allowed_ips(self) -> set:
        """Load allowed IPs from configuration"""
        return set(SECURITY_CONFIG["API_SECURITY"]["ALLOWED_IPS"])

    def validate_api_headers(self, f):
        """Decorator to validate required API headers"""

        @wraps(f)
        async def decorated_function(*args, **kwargs):
            required_headers = SECURITY_CONFIG["API_SECURITY"]["REQUIRED_HEADERS"]
            missing_headers = [
                header for header in required_headers if header not in request.headers
            ]

            if missing_headers:
                return (
                    jsonify(
                        {
                            "error": "Missing required headers",
                            "missing": missing_headers,
                        }
                    ),
                    400,
                )

            return await f(*args, **kwargs)

        return decorated_function

    def require_encryption(self, f):
        """Decorator to ensure request data is encrypted"""

        @wraps(f)
        async def decorated_function(*args, **kwargs):
            try:
                # Check if request data is encrypted
                if request.is_json:
                    encrypted_data = request.get_json()
                    if "encrypted_payload" not in encrypted_data:
                        return jsonify({"error": "Request must be encrypted"}), 400

                    # Decrypt the payload
                    decrypted_data = self.encryption_manager.decrypt(
                        encrypted_data["encrypted_payload"]
                    )
                    if not decrypted_data:
                        return jsonify({"error": "Invalid encryption"}), 400

                    # Replace request data with decrypted data
                    request.data = decrypted_data

                return await f(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Encryption middleware error: {str(e)}")
                return jsonify({"error": "Security check failed"}), 500

        return decorated_function

    def verify_ip_whitelist(self, f):
        """Decorator to verify IP whitelist for IRS submissions"""

        @wraps(f)
        async def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            if client_ip not in self.allowed_ips:
                await self.audit_logger.log_document_access(
                    user_id=request.user.id if request.user else None,
                    document_id=None,
                    access_type="ip_whitelist_violation",
                    success=False,
                    details={"ip_address": client_ip},
                )
                return jsonify({"error": "IP not authorized"}), 403

            return await f(*args, **kwargs)

        return decorated_function

    def audit_request(self, f):
        """Decorator to audit API requests"""

        @wraps(f)
        async def decorated_function(*args, **kwargs):
            try:
                # Log request details
                await self.audit_logger.log_document_access(
                    user_id=request.user.id if request.user else None,
                    document_id=kwargs.get("document_id"),
                    access_type="api_request",
                    success=True,
                    details={
                        "method": request.method,
                        "path": request.path,
                        "ip_address": request.remote_addr,
                        "user_agent": request.user_agent.string,
                    },
                )

                response = await f(*args, **kwargs)

                # Log response status
                await self.audit_logger.log_document_access(
                    user_id=request.user.id if request.user else None,
                    document_id=kwargs.get("document_id"),
                    access_type="api_response",
                    success=response.status_code == 200,
                    details={"status_code": response.status_code},
                )

                return response

            except Exception as e:
                self.logger.error(f"Audit middleware error: {str(e)}")
                raise

        return decorated_function
