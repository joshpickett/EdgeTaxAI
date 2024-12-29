import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

class AuditLogger:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger('audit')

    def log_bank_operation(self, 
                          user_id: int, 
                          operation: str, 
                          details: Dict[str, Any],
                          status: str = 'success',
                          error: Optional[str] = None) -> None:
        """Log bank-related operations"""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'operation': operation,
            'details': details,
            'status': status,
            'error': error
        }
        
        self.logger.info(f"Bank Operation: {log_entry}")
        
        # Store in database if needed
        # self.db.add(AuditLog(**log_entry))
        # self.db.commit()

    def log_security_event(self, 
                          user_id: int,
                          event_type: str,
                          ip_address: str,
                          details: Dict[str, Any]) -> None:
        """Log security-related events"""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'event_type': event_type,
            'ip_address': ip_address,
            'details': details
        }
        
        self.logger.warning(f"Security Event: {log_entry}")
