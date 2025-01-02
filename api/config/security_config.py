from typing import Dict, Any
import os

SECURITY_CONFIG: Dict[str, Any] = {
    "ENCRYPTION": {
        "KEY_ROTATION_DAYS": 30,
        "ALGORITHM": "AES-256-GCM",
        "KEY_LENGTH": 256,
    },
    "ACCESS_CONTROL": {
        "MAX_LOGIN_ATTEMPTS": 5,
        "LOCKOUT_DURATION_MINUTES": 30,
        "PASSWORD_EXPIRY_DAYS": 90,
        "REQUIRE_2FA": True,
    },
    "API_SECURITY": {
        "RATE_LIMIT": {
            "DEFAULT": 100,  # requests per minute
            "IRS_ENDPOINTS": 20,  # requests per minute
            "TAX_CALCULATION": 50,  # requests per minute
        },
        "ALLOWED_IPS": os.getenv("ALLOWED_IPS", "127.0.0.1,::1").split(","),
        "REQUIRED_HEADERS": ["X-API-Key", "X-Request-ID"],
    },
    "AUDIT": {
        "RETENTION_DAYS": 365,
        "SENSITIVE_FIELDS": {
            "ssn",
            "tax_id",
            "bank_account",
            "routing_number",
            "credit_card",
        },
        "EVENT_TYPES": {
            "DOCUMENT_ACCESS": "document_access",
            "TAX_CALCULATION": "tax_calculation",
            "FORM_SUBMISSION": "form_submission",
            "USER_AUTH": "user_auth",
            "SYSTEM": "system",
        },
    },
}
