import logging
from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from .config import Config

class NotificationHandler:
    def __init__(self):
        self.twilio_client = Client(
            Config.TWILIO_ACCOUNT_SID,
            Config.TWILIO_AUTH_TOKEN
        )
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.smtp_username = Config.SMTP_USERNAME
        self.smtp_password = Config.SMTP_PASSWORD
        
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send Short Message Service notification"""
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logging.info(f"Short Message Service sent to {phone_number}")
            return True
        except Exception as e:
            logging.error(f"Short Message Service sending failed: {e}")
            return False
            
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send electronic mail notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logging.info(f"Electronic mail sent to {to_email}")
            return True
        except Exception as e:
            logging.error(f"Electronic mail sending failed: {e}")
            return False
            
    def send_expense_alert(self, user_data: Dict[str, Any]) -> bool:
        """Send expense alert notification"""
        message = (
            f"New expense recorded:\n"
            f"Amount: ${user_data['amount']}\n"
            f"Category: {user_data['category']}\n"
            f"Date: {user_data['date']}"
        )
        
        if user_data.get('phone_number'):
            self.send_sms(user_data['phone_number'], message)
        
        if user_data.get('email'):
            self.send_email(
                user_data['email'],
                "New Expense Recorded",
                message
            )
            
        return True
        
    def send_tax_reminder(self, user_data: Dict[str, Any]) -> bool:
        """Send tax deadline reminder"""
        message = (
            f"Tax Payment Reminder:\n"
            f"Due Date: {user_data['due_date']}\n"
            f"Estimated Amount: ${user_data['estimated_amount']}\n"
            f"Please ensure timely payment to avoid penalties."
        )
        
        return self.send_email(
            user_data['email'],
            "Tax Payment Reminder",
            message
        )
