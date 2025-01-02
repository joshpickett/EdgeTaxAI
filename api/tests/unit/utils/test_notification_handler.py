import pytest
from unittest.mock import Mock, patch
from api.utils.notification_handler import NotificationHandler
from twilio.rest import Client


@pytest.fixture
def notification_handler():
    return NotificationHandler()


@pytest.fixture
def mock_twilio():
    with patch("twilio.rest.Client") as mock:
        yield mock


@pytest.fixture
def mock_smtp():
    with patch("smtplib.SMTP") as mock:
        yield mock


def test_send_sms_success(notification_handler, mock_twilio):
    """Test successful SMS sending"""
    phone_number = "+1234567890"
    message = "Test message"

    result = notification_handler.send_sms(phone_number, message)

    assert result is True
    mock_twilio.return_value.messages.create.assert_called_once_with(
        body=message, from_=notification_handler.twilio_phone_number, to=phone_number
    )


def test_send_sms_failure(notification_handler, mock_twilio):
    """Test SMS sending failure"""
    mock_twilio.return_value.messages.create.side_effect = Exception("SMS failed")

    result = notification_handler.send_sms("+1234567890", "Test message")

    assert result is False


def test_send_email_success(notification_handler, mock_smtp):
    """Test successful email sending"""
    email = "test@example.com"
    subject = "Test Subject"
    body = "Test body"

    result = notification_handler.send_email(email, subject, body)

    assert result is True
    mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()


def test_send_email_failure(notification_handler, mock_smtp):
    """Test email sending failure"""
    mock_smtp.return_value.__enter__.return_value.send_message.side_effect = Exception(
        "Email failed"
    )

    result = notification_handler.send_email("test@example.com", "Test", "Body")

    assert result is False


def test_send_expense_alert_success(notification_handler):
    """Test successful expense alert sending"""
    with patch.object(notification_handler, "send_sms") as mock_sms, patch.object(
        notification_handler, "send_email"
    ) as mock_email:

        user_data = {
            "phone_number": "+1234567890",
            "email": "test@example.com",
            "amount": 100.00,
            "category": "Food",
            "date": "2023-01-01",
        }

        result = notification_handler.send_expense_alert(user_data)

        assert result is True
        mock_sms.assert_called_once()
        mock_email.assert_called_once()


def test_send_expense_alert_partial(notification_handler):
    """Test expense alert with partial contact info"""
    with patch.object(notification_handler, "send_sms") as mock_sms, patch.object(
        notification_handler, "send_email"
    ) as mock_email:

        user_data = {
            "email": "test@example.com",
            "amount": 100.00,
            "category": "Food",
            "date": "2023-01-01",
        }

        result = notification_handler.send_expense_alert(user_data)

        assert result is True
        mock_sms.assert_not_called()
        mock_email.assert_called_once()


def test_send_tax_reminder_success(notification_handler):
    """Test successful tax reminder sending"""
    with patch.object(notification_handler, "send_email") as mock_email:
        user_data = {
            "email": "test@example.com",
            "due_date": "2023-04-15",
            "estimated_amount": 1000.00,
        }

        result = notification_handler.send_tax_reminder(user_data)

        assert result is True
        mock_email.assert_called_once()


def test_send_tax_reminder_failure(notification_handler):
    """Test tax reminder sending failure"""
    with patch.object(notification_handler, "send_email") as mock_email:
        mock_email.return_value = False

        user_data = {
            "email": "test@example.com",
            "due_date": "2023-04-15",
            "estimated_amount": 1000.00,
        }

        result = notification_handler.send_tax_reminder(user_data)

        assert result is False


def test_message_formatting(notification_handler, mock_smtp):
    """Test email message formatting"""
    email = "test@example.com"
    subject = "Test Subject"
    body = "Test body"

    notification_handler.send_email(email, subject, body)

    # Verify email formatting
    call_args = mock_smtp.return_value.__enter__.return_value.send_message.call_args
    message = call_args[0][0]

    assert message["Subject"] == subject
    assert message["To"] == email
    assert message["From"] == notification_handler.smtp_username
