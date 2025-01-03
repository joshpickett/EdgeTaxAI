from typing import Dict, Any
from datetime import datetime
import uuid
from api.utils.audit_logger import AuditLogger

class ErrorHandler:
    def __init__(self):
        self.audit_logger = AuditLogger()

    def handle_auth_error(self, error: Exception, user_id: str = None) -> Dict[str, Any]:
        error_id = str(uuid.uuid4())
        self.audit_logger.log_error(error_id, str(error), user_id)
        
        return {
            'error_id': error_id,
            'message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'type': error.__class__.__name__
        }
