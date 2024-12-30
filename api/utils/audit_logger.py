from typing import Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.audit_log import AuditLog
from api.utils.encryption_utils import EncryptionManager

class AuditLogger:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.encryption_manager = EncryptionManager()
        self.sensitive_fields = {'ssn', 'tax_id', 'bank_account', 'routing_number'}

    async def log_document_submission(
        self,
        user_id: int,
        document_id: int,
        submission_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log document submission events with enhanced security"""
        try:
            # Enhanced logging implementation
            
        except Exception as e:
            self.logger.error(f"Error logging document submission: {str(e)}")
            raise

    async def log_tax_calculation(
        self,
        user_id: int,
        calculation_type: str,
        input_data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Log tax calculation events"""
        try:
            # Sanitize sensitive data
            sanitized_input = self._sanitize_sensitive_data(input_data)
            sanitized_result = self._sanitize_sensitive_data(result)

            audit_entry = AuditLog(
                user_id=user_id,
                event_type="tax_calculation",
                event_subtype=calculation_type,
                details={
                    'input': sanitized_input,
                    'result': sanitized_result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging tax calculation: {str(e)}")
            raise

    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive fields in the data"""
        return {key: (self.encryption_manager.encrypt(value) if key in self.sensitive_fields else value) for key, value in data.items()}
