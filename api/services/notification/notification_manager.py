from typing import Dict, Any, List
import logging
from datetime import datetime
from api.config.notification_config import NOTIFICATION_CONFIG
from api.models.notifications import Notification, NotificationType
from api.services.email_service import EmailService

class NotificationManager:
    """Manage system notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_service = EmailService()
        
        self.notification_types = {
            'EXPIRATION': {
                'priority': 'high',
                'channels': ['email', 'in_app'],
                'template': 'document_expiration'
            },
            'VALIDATION': {
                'priority': 'medium',
                'channels': ['in_app'],
                'template': 'validation_error'
            },
            'STATUS_CHANGE': {
                'priority': 'low',
                'channels': ['in_app'],
                'template': 'status_change'
            }
        }

    async def send_notification(
        self,
        user_id: int,
        notification_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification to user"""
        try:
            notification_config = self.notification_types.get(notification_type)
            if not notification_config:
                raise ValueError(f"Invalid notification type: {notification_type}")
            
            # Create notification record
            notification = await self._create_notification(
                user_id,
                notification_type,
                notification_config,
                data
            )
            
            # Send through appropriate channels
            for channel in notification_config['channels']:
                await self._send_through_channel(
                    notification,
                    channel,
                    notification_config
                )
            
            return {
                'notification_id': notification.id,
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
            raise

    async def _create_notification(
        self,
        user_id: int,
        notification_type: str,
        config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Notification:
        """Create notification record"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            priority=config['priority'],
            data=data,
            status='pending'
        )
        
        # Save to database
        await notification.save()
        return notification

    async def _send_through_channel(
        self,
        notification: Notification,
        channel: str,
        config: Dict[str, Any]
    ) -> None:
        """Send notification through specific channel"""
        if channel == 'email':
            await self._send_email_notification(notification, config)
        elif channel == 'in_app':
            await self._send_in_app_notification(notification)

    async def _send_email_notification(
        self,
        notification: Notification,
        config: Dict[str, Any]
    ) -> None:
        """Send email notification"""
        template = config['template']
        await self.email_service.send_templated_email(
            notification.user_id,
            template,
            notification.data
        )

    async def _send_in_app_notification(
        self,
        notification: Notification
    ) -> None:
        """Send in-app notification"""
        # Implementation would depend on your frontend notification system
        notification.status = 'delivered'
        await notification.save()

    async def get_user_notifications(
        self,
        user_id: int,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        query = {'user_id': user_id}
        if filters:
            query.update(filters)
            
        notifications = await Notification.find(query)
        return [notification.to_dict() for notification in notifications]
