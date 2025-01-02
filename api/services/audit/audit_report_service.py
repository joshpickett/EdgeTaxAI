from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.models.audit_log import AuditLog
from api.config.security_config import SECURITY_CONFIG


class AuditReportService:
    """Service for generating audit reports"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.event_types = SECURITY_CONFIG["AUDIT"]["EVENT_TYPES"]

    async def generate_activity_report(
        self, start_date: datetime, end_date: datetime, filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate activity report for date range"""
        try:
            query = self.db.query(AuditLog).filter(
                AuditLog.created_at.between(start_date, end_date)
            )

            if filters:
                if filters.get("event_type"):
                    query = query.filter(AuditLog.event_type == filters["event_type"])
                if filters.get("user_id"):
                    query = query.filter(AuditLog.user_id == filters["user_id"])

            audit_logs = await query.all()

            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "total_events": len(audit_logs),
                "events_by_type": self._group_by_event_type(audit_logs),
                "timeline": self._generate_timeline(audit_logs),
                "summary": self._generate_summary(audit_logs),
            }

        except Exception as e:
            self.logger.error(f"Error generating activity report: {str(e)}")
            raise

    async def generate_security_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate security-focused audit report"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            security_events = (
                await self.db.query(AuditLog)
                .filter(
                    AuditLog.created_at.between(start_date, end_date),
                    AuditLog.event_type.in_(
                        [
                            self.event_types["USER_AUTH"],
                            self.event_types["DOCUMENT_ACCESS"],
                            self.event_types["SYSTEM"],
                        ]
                    ),
                )
                .all()
            )

            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "total_events": len(security_events),
                "events_by_type": self._group_by_event_type(security_events),
                "ip_analysis": self._analyze_ip_addresses(security_events),
                "user_agent_analysis": self._analyze_user_agents(security_events),
                "recommendations": self._generate_security_recommendations(
                    security_events
                ),
            }

        except Exception as e:
            self.logger.error(f"Error generating security report: {str(e)}")
            raise

    def _group_by_event_type(self, audit_logs: List[AuditLog]) -> Dict[str, int]:
        """Group audit logs by event type"""
        event_counts = {}
        for log in audit_logs:
            event_counts[log.event_type] = event_counts.get(log.event_type, 0) + 1
        return event_counts

    def _generate_timeline(self, audit_logs: List[AuditLog]) -> List[Dict[str, Any]]:
        """Generate timeline of events"""
        timeline = []
        for log in sorted(audit_logs, key=lambda x: x.created_at):
            timeline.append(
                {
                    "timestamp": log.created_at.isoformat(),
                    "event_type": log.event_type,
                    "user_id": log.user_id,
                    "summary": self._generate_event_summary(log),
                }
            )
        return timeline

    def _generate_event_summary(self, log: AuditLog) -> str:
        """Generate human-readable summary of event"""
        event_data = log.event_data or {}

        if log.event_type == self.event_types["STATUS_CHANGE"]:
            return f"Document status changed from {event_data.get('old_status')} to {event_data.get('new_status')}"
        elif log.event_type == self.event_types["DOCUMENT_ACCESS"]:
            return f"Document {event_data.get('document_id')} accessed"
        elif log.event_type == self.event_types["USER_AUTH"]:
            return f"User authentication event: {event_data.get('action', 'unknown')}"

        return "Event occurred"

    def _analyze_ip_addresses(self, audit_logs: List[AuditLog]) -> Dict[str, Any]:
        """Analyze IP addresses in audit logs"""
        ip_counts = {}
        for log in audit_logs:
            if log.ip_address:
                ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

        return {
            "unique_ips": len(ip_counts),
            "ip_frequency": ip_counts,
            "suspicious_activity": self._detect_suspicious_ips(ip_counts),
        }

    def _analyze_user_agents(self, audit_logs: List[AuditLog]) -> Dict[str, Any]:
        """Analyze user agents in audit logs"""
        agent_counts = {}
        for log in audit_logs:
            if log.user_agent:
                agent_counts[log.user_agent] = agent_counts.get(log.user_agent, 0) + 1

        return {
            "unique_agents": len(agent_counts),
            "agent_frequency": agent_counts,
            "suspicious_activity": self._detect_suspicious_agents(agent_counts),
        }

    def _detect_suspicious_ips(self, ip_counts: Dict[str, int]) -> List[Dict[str, Any]]:
        """Detect suspicious IP activity"""
        suspicious = []
        threshold = 100  # Configurable threshold

        for ip, count in ip_counts.items():
            if count > threshold:
                suspicious.append(
                    {
                        "ip_address": ip,
                        "event_count": count,
                        "reason": f"High activity: {count} events",
                    }
                )

        return suspicious

    def _detect_suspicious_agents(
        self, agent_counts: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Detect suspicious user agent activity"""
        suspicious = []
        for agent, count in agent_counts.items():
            if self._is_suspicious_agent(agent):
                suspicious.append(
                    {
                        "user_agent": agent,
                        "event_count": count,
                        "reason": "Suspicious user agent pattern",
                    }
                )
        return suspicious

    def _is_suspicious_agent(self, user_agent: str) -> bool:
        """Check if user agent looks suspicious"""
        suspicious_patterns = [
            "bot",
            "crawler",
            "spider",
            "curl",
            "wget",
            "python-requests",
        ]
        return any(pattern in user_agent.lower() for pattern in suspicious_patterns)

    def _generate_security_recommendations(
        self, audit_logs: List[AuditLog]
    ) -> List[Dict[str, Any]]:
        """Generate security recommendations based on audit logs"""
        recommendations = []

        # Check for suspicious patterns
        ip_analysis = self._analyze_ip_addresses(audit_logs)
        if ip_analysis["suspicious_activity"]:
            recommendations.append(
                {
                    "type": "security_alert",
                    "priority": "high",
                    "message": "Suspicious IP activity detected",
                    "details": ip_analysis["suspicious_activity"],
                }
            )

        # Add more recommendation logic as needed

        return recommendations

    def _generate_summary(self, audit_logs: List[AuditLog]) -> Dict[str, Any]:
        """Generate summary statistics"""
        return {
            "total_events": len(audit_logs),
            "unique_users": len(set(log.user_id for log in audit_logs if log.user_id)),
            "event_types": self._group_by_event_type(audit_logs),
            "peak_activity": self._find_peak_activity(audit_logs),
        }

    def _find_peak_activity(self, audit_logs: List[AuditLog]) -> Dict[str, Any]:
        """Find peak activity periods"""
        if not audit_logs:
            return {}

        hourly_counts = {}
        for log in audit_logs:
            hour = log.created_at.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])
        return {"timestamp": peak_hour[0].isoformat(), "event_count": peak_hour[1]}
