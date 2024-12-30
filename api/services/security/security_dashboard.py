from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.models.audit_log import AuditLog
from api.config.security_config import SECURITY_CONFIG

class SecurityDashboard:
    """Security dashboard data and metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get security dashboard metrics"""
        try:
            return {
                'alerts': await self._get_recent_alerts(),
                'events': await self._get_security_events(),
                'threats': await self._get_threat_metrics(),
                'compliance': await self._get_compliance_metrics()
            }
        except Exception as e:
            self.logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise
            
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent security alerts"""
        try:
            alerts = await self.db.query(AuditLog).filter(
                AuditLog.severity.in_(['HIGH', 'CRITICAL'])
            ).order_by(
                AuditLog.timestamp.desc()
            ).limit(10).all()
            
            return [{
                'id': alert.id,
                'type': alert.event_type,
                'severity': alert.severity,
                'timestamp': alert.timestamp.isoformat(),
                'details': alert.event_data
            } for alert in alerts]
            
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {str(e)}")
            return []
            
    async def _get_security_events(self) -> Dict[str, Any]:
        """Get security event statistics"""
        try:
            today = datetime.utcnow()
            week_ago = today - timedelta(days=7)
            
            events = await self.db.query(AuditLog).filter(
                AuditLog.timestamp >= week_ago
            ).all()
            
            return {
                'total': len(events),
                'by_type': self._group_events_by_type(events),
                'by_severity': self._group_events_by_severity(events),
                'timeline': self._create_event_timeline(events)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security events: {str(e)}")
            return {}
            
    async def _get_threat_metrics(self) -> Dict[str, Any]:
        """Get threat detection metrics"""
        try:
            return {
                'authentication_failures': await self._count_auth_failures(),
                'api_abuse_attempts': await self._count_api_abuse(),
                'suspicious_ips': await self._count_suspicious_ips()
            }
        except Exception as e:
            self.logger.error(f"Error getting threat metrics: {str(e)}")
            return {}
            
    async def _get_compliance_metrics(self) -> Dict[str, Any]:
        """Get compliance-related metrics"""
        try:
            return {
                'encryption_status': await self._check_encryption_status(),
                'audit_coverage': await self._calculate_audit_coverage(),
                'policy_violations': await self._count_policy_violations()
            }
        except Exception as e:
            self.logger.error(f"Error getting compliance metrics: {str(e)}")
            return {}
            
    def _group_events_by_type(self, events: List[AuditLog]) -> Dict[str, int]:
        """Group events by type"""
        grouped = {}
        for event in events:
            if event.event_type not in grouped:
                grouped[event.event_type] = 0
            grouped[event.event_type] += 1
        return grouped
        
    def _group_events_by_severity(self, events: List[AuditLog]) -> Dict[str, int]:
        """Group events by severity"""
        grouped = {}
        for event in events:
            if event.severity not in grouped:
                grouped[event.severity] = 0
            grouped[event.severity] += 1
        return grouped
        
    def _create_event_timeline(self, events: List[AuditLog]) -> List[Dict[str, Any]]:
        """Create timeline of security events"""
        timeline = []
        for event in events:
            timeline.append({
                'timestamp': event.timestamp.isoformat(),
                'type': event.event_type,
                'severity': event.severity,
                'summary': self._create_event_summary(event)
            })
        return sorted(timeline, key=lambda x: x['timestamp'])
        
    def _create_event_summary(self, event: AuditLog) -> str:
        """Create summary of security event"""
        return f"{event.event_type} event from {event.ip_address}"
