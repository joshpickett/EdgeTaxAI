from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

class BankAuditLogger:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger('bank_audit')

    def log_connection_attempt(self, 
                             user_id: int, 
                             bank_name: str,
                             status: str,
                             error: Optional[str] = None) -> None:
        """Log bank connection attempts"""
        self._log_event(
            user_id=user_id,
            event_type="connection_attempt",
            details={
                "bank_name": bank_name,
                "status": status,
                "error": error
            }
        )

    def log_transaction_sync(self,
                           user_id: int,
                           bank_account_id: int,
                           transaction_count: int,
                           status: str) -> None:
        """Log transaction synchronization"""
        self._log_event(
            user_id=user_id,
            event_type="transaction_sync",
            details={
                "bank_account_id": bank_account_id,
                "transaction_count": transaction_count,
                "status": status
            }
        )

    def _log_event(self,
                   user_id: int,
                   event_type: str,
                   details: Dict[str, Any]) -> None:
        """Internal method to log events"""
        log_entry = {
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "event_type": event_type,
            "details": details
        }
        
        self.logger.info(f"Bank Audit: {log_entry}")
