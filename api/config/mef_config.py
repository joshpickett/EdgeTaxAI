import os
from typing import Dict, Any

MEF_CONFIG: Dict[str, Any] = {
    "ENDPOINTS": {
        "PRODUCTION": "https://la.www4.irs.gov/a2a/mef",
        "TEST": "https://la.alt.www4.irs.gov/a2a/mef",
        "STATUS": "https://la.www4.irs.gov/a2a/mef/status",
    },
    "CREDENTIALS": {
        "API_KEY": os.getenv("IRS_API_KEY"),
        "PROVIDER_ID": os.getenv("IRS_PROVIDER_ID"),
        "CERTIFICATE_PATH": os.getenv("IRS_CERT_PATH"),
        "PRIVATE_KEY_PATH": os.getenv("IRS_PRIVATE_KEY_PATH"),
    },
    "TRANSMISSION": {"MAX_RETRIES": 3, "TIMEOUT": 300, "BATCH_SIZE": 100},
    "VALIDATION": {
        "SCHEMA_PATH": "api/schemas/mef/",
        "MAX_FILE_SIZE": 10 * 1024 * 1024,  # 10MB
        "ALLOWED_NAMESPACES": [
            "http://www.irs.gov/efile",
            "http://www.w3.org/2001/XMLSchema-instance",
        ],
        "SCHEMA_VERSIONS": {
            "SCHEDULE_C": "2023v1.0",
            "1099_NEC": "2023v1.0",
            "1099_K": "2023v1.0",
        },
    },
}
