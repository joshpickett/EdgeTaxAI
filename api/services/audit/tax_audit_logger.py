from typing import Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from api.models.audit_log import AuditLog
from api.config.security_config import SECURITY_CONFIG

class TaxAuditLogger:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.event_types = SECURITY_CONFIG['AUDIT']['EVENT_TYPES']

    async def log_tax_calculation(self, 
                                user_id: int,
                                calculation_type: str,
                                input_data: Dict[str, Any],
                                result: Dict[str, Any]) -> None:
        """Log tax calculation events"""
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                event_type=self.event_types['TAX_CALCULATION'],
                event_data={
                    'calculation_type': calculation_type,
                    'input_summary': self._sanitize_input(input_data),
                    'result_summary': self._sanitize_result(result),
                    'timestamp': datetime.utcnow().isoformat()
                },
                ip_address=self._get_client_ip(),
                user_agent=self._get_user_agent()
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging tax calculation: {str(e)}")
            raise

    async def log_form_submission(self,
                                user_id: int,
                                form_type: str,
                                form_data: Dict[str, Any],
                                submission_id: str) -> None:
        """Log tax form submission events"""
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                event_type=self.event_types['FORM_SUBMISSION'],
                event_data={
                    'form_type': form_type,
                    'submission_id': submission_id,
                    'form_summary': self._sanitize_form_data(form_data),
                    'timestamp': datetime.utcnow().isoformat()
                },
                ip_address=self._get_client_ip(),
                user_agent=self._get_user_agent()
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging form submission: {str(e)}")
            raise

    async def log_status_change(self,
                               document_id: int,
                               old_status: str,
                               new_status: str,
                               metadata: Dict[str, Any] = None) -> None:
        """Log document status changes"""
        try:
            audit_entry = AuditLog(
                event_type=self.event_types['STATUS_CHANGE'],
                event_data={
                    'document_id': document_id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'metadata': metadata,
                    'timestamp': datetime.utcnow().isoformat()
                },
                ip_address=self._get_client_ip(),
                user_agent=self._get_user_agent()
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
        except Exception as e:
            self.logger.error(f"Error logging status change: {str(e)}")
            raise

    def _sanitize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from input data"""
        sanitized = input_data.copy()
        for field in SECURITY_CONFIG['AUDIT']['SENSITIVE_FIELDS']:
            if field in sanitized:
                sanitized[field] = '***REDACTED***'
        return sanitized

    def _sanitize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize calculation results"""
        return {
            'calculation_id': result.get('id'),
            'timestamp': result.get('timestamp'),
            'status': result.get('status')
        }

    def _sanitize_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize form data for audit logs"""
        return {
            'form_id': form_data.get('id'),
            'timestamp': datetime.utcnow().isoformat(),
            'field_count': len(form_data.keys())
        }

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Implementation depends on your web framework
        return "0.0.0.0"

    def _get_user_agent(self) -> str:
        """Get user agent string"""
        # Implementation depends on your web framework
        return "Unknown"
