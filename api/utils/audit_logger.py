import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from api.models.audit_log import AuditLog

class AuditLogger:
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.logger = logging.getLogger('audit')

    def log_auth_event(self, 
                      user_id: str, 
                      event_type: str, 
                      status: str,
                      details: Dict[str, Any],
                      ip_address: str,
                      device_fingerprint: str) -> None:
        """Log authentication related events"""
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                event_type=event_type,
                status=status,
                details=details,
                ip_address=ip_address,
                device_fingerprint=device_fingerprint,
                timestamp=datetime.utcnow()
            )
            
            if self.db:
                self.db.add(audit_entry)
                self.db.commit()
            
            self.logger.info(
                f"Auth event: {event_type} | User: {user_id} | "
                f"Status: {status} | IP: {ip_address}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {str(e)}")

    def log_security_event(self, 
                          event_type: str,
                          severity: str,
                          details: Dict[str, Any]) -> None:
        """Log security-related events"""
        try:
            self.logger.warning(
                f"Security event: {event_type} | "
                f"Severity: {severity} | "
                f"Details: {details}"
            )
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")
