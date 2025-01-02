import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from api.utils.otp_manager import OTPManager


@pytest.fixture
def otp_manager():
    return OTPManager()


@pytest.fixture
def mock_database():
    with patch("api.utils.otp_manager.get_db_connection") as mock:
        yield mock


def test_generate_one_time_password(otp_manager):
    """Test one time password generation"""
    one_time_password = otp_manager.generate_otp()
    assert len(one_time_password) == 6
    assert one_time_password.isdigit()
    assert len(set(one_time_password)) > 1  # Ensure some randomness


def test_save_one_time_password_success(otp_manager, mock_database):
    """Test successful one time password saving"""
    mock_cursor = Mock()
    mock_database.return_value.cursor.return_value = mock_cursor

    result = otp_manager.save_otp(1, "123456")

    assert result is True
    mock_cursor.execute.assert_called_once()
    mock_database.return_value.commit.assert_called_once()


def test_save_one_time_password_failure(otp_manager, mock_database):
    """Test one time password saving failure"""
    mock_database.return_value.cursor.side_effect = Exception("Database error")

    result = otp_manager.save_otp(1, "123456")

    assert result is False


def test_verify_one_time_password_success(otp_manager, mock_database):
    """Test successful one time password verification"""
    mock_cursor = Mock()
    # Mock stored one time password with future expiry
    future_time = (datetime.now() + timedelta(minutes=5)).isoformat()
    mock_cursor.fetchone.return_value = ("123456", future_time)
    mock_database.return_value.cursor.return_value = mock_cursor

    result, message = otp_manager.verify_otp(1, "123456")

    assert result is True
    assert message is None


def test_verify_one_time_password_expired(otp_manager, mock_database):
    """Test expired one time password verification"""
    mock_cursor = Mock()
    # Mock stored one time password with past expiry
    past_time = (datetime.now() - timedelta(minutes=5)).isoformat()
    mock_cursor.fetchone.return_value = ("123456", past_time)
    mock_database.return_value.cursor.return_value = mock_cursor

    result, message = otp_manager.verify_otp(1, "123456")

    assert result is False
    assert "expired" in message.lower()


def test_verify_one_time_password_invalid(otp_manager, mock_database):
    """Test invalid one time password verification"""
    mock_cursor = Mock()
    future_time = (datetime.now() + timedelta(minutes=5)).isoformat()
    mock_cursor.fetchone.return_value = ("123456", future_time)
    mock_database.return_value.cursor.return_value = mock_cursor

    result, message = otp_manager.verify_otp(1, "654321")

    assert result is False
    assert "invalid" in message.lower()


def test_verify_one_time_password_user_not_found(otp_manager, mock_database):
    """Test one time password verification for non-existent user"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = None
    mock_database.return_value.cursor.return_value = mock_cursor

    result, message = otp_manager.verify_otp(1, "123456")

    assert result is False
    assert "not found" in message.lower()


def test_verify_one_time_password_database_error(otp_manager, mock_database):
    """Test one time password verification with database error"""
    mock_database.return_value.cursor.side_effect = Exception("Database error")

    result, message = otp_manager.verify_otp(1, "123456")

    assert result is False
    assert "failed" in message.lower()
