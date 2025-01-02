from typing import Dict, Any, List
import logging
from datetime import datetime
import smtplib
import requests
from email.mime.text import MIMEText
from api.config.security_config import SECURITY_CONFIG


class AlertManager:
    """Manage security alerts and notifications"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_config = SECURITY_CONFIG["ALERTS"]["EMAIL"]
        self.sms_config = SECURITY_CONFIG["ALERTS"]["SMS"]
        self.alert_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

    async def trigger_alert(
        self, alert_type: str, severity: str, details: Dict[str, Any]
    ) -> None:
        """Trigger an alert based on severity and type"""
        try:
            alert_data = {
                "type": alert_type,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
            }

            # Determine notification channels based on severity
            if self.alert_levels[severity] >= self.alert_levels["HIGH"]:
                await self._send_urgent_alert(alert_data)
            else:
                await self._send_standard_alert(alert_data)

        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")

    async def _send_urgent_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send urgent alert through all channels"""
        try:
            await self._send_email_alert(alert_data)
            await self._send_sms_alert(alert_data)
            await self._send_dashboard_notification(alert_data)
        except Exception as e:
            self.logger.error(f"Error sending urgent alert: {str(e)}")

    async def _send_standard_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send standard alert through email and dashboard"""
        try:
            await self._send_email_alert(alert_data)
            await self._send_dashboard_notification(alert_data)
        except Exception as e:
            self.logger.error(f"Error sending standard alert: {str(e)}")

    async def _send_email_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send email alert"""
        try:
            msg = MIMEText(self._format_alert_message(alert_data))
            msg["Subject"] = (
                f"Security Alert: {alert_data['type']} - {alert_data['severity']}"
            )
            msg["From"] = self.email_config["FROM_ADDRESS"]
            msg["To"] = self.email_config["TO_ADDRESS"]

            with smtplib.SMTP(self.email_config["SMTP_SERVER"]) as server:
                server.starttls()
                server.login(
                    self.email_config["USERNAME"], self.email_config["PASSWORD"]
                )
                server.send_message(msg)

        except Exception as e:
            self.logger.error(f"Error sending email alert: {str(e)}")

    async def _send_sms_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send SMS alert"""
        try:
            message = self._format_alert_message(alert_data, sms=True)

            response = requests.post(
                self.sms_config["API_URL"],
                json={"to": self.sms_config["TO_NUMBER"], "message": message},
                headers={"Authorization": f"Bearer {self.sms_config['API_KEY']}"},
            )

            if not response.ok:
                raise Exception(f"SMS API error: {response.text}")

        except Exception as e:
            self.logger.error(f"Error sending SMS alert: {str(e)}")

    async def _send_dashboard_notification(self, alert_data: Dict[str, Any]) -> None:
        """Send alert to security dashboard"""
        try:
            # Implementation for real-time dashboard notifications
            # This could use WebSocket or Server-Sent Events
            pass
        except Exception as e:
            self.logger.error(f"Error sending dashboard notification: {str(e)}")

    def _format_alert_message(
        self, alert_data: Dict[str, Any], sms: bool = False
    ) -> str:
        """Format alert message based on channel"""
        if sms:
            return (
                f"SECURITY ALERT: {alert_data['type']}\n"
                f"Severity: {alert_data['severity']}\n"
                f"Time: {alert_data['timestamp']}"
            )

        return (
            f"Security Alert Details:\n"
            f"Type: {alert_data['type']}\n"
            f"Severity: {alert_data['severity']}\n"
            f"Time: {alert_data['timestamp']}\n"
            f"Details: {alert_data['details']}"
        )
