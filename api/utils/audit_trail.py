import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from api.config.database import SessionLocal


class AuditLogger:
    def __init__(self):
        self.db = SessionLocal()

    def log_tax_analysis(
        self, user_id: str, action: str, details: Dict[str, Any]
    ) -> None:
        """Log tax analysis operations"""
        self.logger.info(
            f"Tax Analysis - User: {self._mask_identifier(str(user_id))}, "
            f"Action: {action}, "
            f"Details: {details}"
        )

    def _setup_logger(self):
        self.logger = logging.getLogger("audit_trail")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("audit_trail.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_auth_attempt(self, identifier: str, action: str) -> None:
        """Log authentication attempts"""
        self.logger.info(
            f"Auth attempt - Action: {action}, Identifier: {self._mask_identifier(identifier)}"
        )

    def log_auth_failure(self, identifier: str, reason: str) -> None:
        """Log authentication failures"""
        self.logger.warning(
            f"Auth failure - Reason: {reason}, Identifier: {self._mask_identifier(identifier)}"
        )

    def log_auth_success(self, identifier: str, action: str) -> None:
        """Log successful authentication"""
        self.logger.info(
            f"Auth success - Action: {action}, Identifier: {self._mask_identifier(identifier)}"
        )

    def _mask_identifier(self, identifier: str) -> str:
        """Mask sensitive information in logs"""
        if "@" in identifier:
            username, domain = identifier.split("@")
            return f"{username[:2]}***@{domain}"
        return f"{identifier[:2]}***{identifier[-2:]}"
