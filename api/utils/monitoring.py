import logging
from datetime import datetime
from typing import Dict, Any, Optional


class MonitoringSystem:
    def __init__(self):
        self.logger = logging.getLogger("monitoring")

    def log_security_event(
        self, event_type: str, details: Dict[str, Any], severity: str = "info"
    ) -> None:
        """Log security-related events"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "security",
            "event": event_type,
            "severity": severity,
            "details": details,
        }
        self.logger.warning(f"Security Event: {log_entry}")

    def log_performance_metric(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
    ) -> None:
        """Log performance metrics"""
        if end_time is None:
            end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "performance",
            "metric": metric_name,
            "duration": duration,
        }
        self.logger.info(f"Performance Metric: {log_entry}")

    def alert(self, severity: str, message: str, context: Dict[str, Any]) -> None:
        """Send alerts for critical events"""
        alert_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "alert",
            "severity": severity,
            "message": message,
            "context": context,
        }
        self.logger.error(f"Alert: {alert_entry}")
