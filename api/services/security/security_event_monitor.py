from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.models.audit_log import AuditLog
from api.config.security_config import SECURITY_CONFIG
from .security_event_logger import SecurityEventLogger

class SecurityEventMonitor:
    """Monitor and analyze security events"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.event_logger = SecurityEventLogger(db)
        self.patterns = {
            'authentication_failure': {
                'threshold': 5,
                'window_minutes': 15
            },
            'application_programming_interface_abuse': {
                'threshold': 100,
                'window_minutes': 1
            },
            'suspicious_internet_protocol': {
                'threshold': 10,
                'window_minutes': 5
            }
        }
        
    async def monitor_events(self) -> None:
        """Monitor security events for patterns"""
        try:
            await self._check_authentication_patterns()
            await self._check_application_programming_interface_abuse_patterns()
            await self._check_suspicious_internet_protocols()
            
        except Exception as e:
            self.logger.error(f"Error monitoring security events: {str(e)}")
            
    async def _check_authentication_patterns(self) -> None:
        """Check for suspicious authentication patterns"""
        window = datetime.utcnow() - timedelta(
            minutes=self.patterns['authentication_failure']['window_minutes']
        )
        
        authentication_failures = await self._get_recent_events(
            event_type='USER_AUTH',
            success=False,
            since=window
        )
        
        # Group by user and IP
        grouped_failures = self._group_events_by_key(
            authentication_failures,
            ['user_id', 'ip_address']
        )
        
        for key, events in grouped_failures.items():
            if len(events) >= self.patterns['authentication_failure']['threshold']:
                await self._handle_authentication_abuse(events)
                
    async def _check_application_programming_interface_abuse_patterns(self) -> None:
        """Check for application programming interface abuse patterns"""
        window = datetime.utcnow() - timedelta(
            minutes=self.patterns['application_programming_interface_abuse']['window_minutes']
        )
        
        application_programming_interface_requests = await self._get_recent_events(
            event_type='API_REQUEST',
            since=window
        )
        
        # Group by IP
        grouped_requests = self._group_events_by_key(
            application_programming_interface_requests,
            ['ip_address']
        )
        
        for key, events in grouped_requests.items():
            if len(events) >= self.patterns['application_programming_interface_abuse']['threshold']:
                await self._handle_application_programming_interface_abuse(events)
                
    async def _check_suspicious_internet_protocols(self) -> None:
        """Check for suspicious IP patterns"""
        window = datetime.utcnow() - timedelta(
            minutes=self.patterns['suspicious_internet_protocol']['window_minutes']
        )
        
        suspicious_events = await self._get_recent_events(
            event_type='SUSPICIOUS_IP',
            since=window
        )
        
        # Group by IP
        grouped_events = self._group_events_by_key(
            suspicious_events,
            ['ip_address']
        )
        
        for key, events in grouped_events.items():
            if len(events) >= self.patterns['suspicious_internet_protocol']['threshold']:
                await self._handle_suspicious_ip(events)
                
    async def _get_recent_events(self,
                               event_type: str,
                               since: datetime,
                               success: bool = None) -> List[AuditLog]:
        """Get recent events of specified type"""
        query = self.db.query(AuditLog).filter(
            AuditLog.event_type == event_type,
            AuditLog.timestamp >= since
        )
        
        if success is not None:
            query = query.filter(AuditLog.success == success)
            
        return await query.all()
        
    def _group_events_by_key(self,
                            events: List[AuditLog],
                            key_fields: List[str]) -> Dict[str, List[AuditLog]]:
        """Group events by specified key fields"""
        grouped = {}
        for event in events:
            key = tuple(event.event_data.get(field) for field in key_fields)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(event)
        return grouped
        
    async def _handle_authentication_abuse(self, events: List[AuditLog]) -> None:
        """Handle authentication abuse detection"""
        await self.event_logger.log_security_event(
            event_type='AUTH_ABUSE_DETECTED',
            user_id=events[0].user_id,
            severity='HIGH',
            details={
                'event_count': len(events),
                'ip_address': events[0].ip_address,
                'first_attempt': events[0].timestamp.isoformat(),
                'last_attempt': events[-1].timestamp.isoformat()
            }
        )
        
    async def _handle_application_programming_interface_abuse(self, events: List[AuditLog]) -> None:
        """Handle application programming interface abuse detection"""
        await self.event_logger.log_security_event(
            event_type='API_ABUSE_DETECTED',
            user_id=events[0].user_id,
            severity='HIGH',
            details={
                'request_count': len(events),
                'ip_address': events[0].ip_address,
                'endpoints': list(set(e.event_data.get('endpoint') for e in events))
            }
        )
        
    async def _handle_suspicious_ip(self, events: List[AuditLog]) -> None:
        """Handle suspicious IP detection"""
        await self.event_logger.log_security_event(
            event_type='SUSPICIOUS_IP_DETECTED',
            user_id=events[0].user_id,
            severity='HIGH',
            details={
                'event_count': len(events),
                'ip_address': events[0].ip_address,
                'event_types': list(set(e.event_type for e in events))
            }
        )
