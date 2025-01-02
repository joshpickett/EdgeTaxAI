import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from desktop.account_creation import account_creation_page


@pytest.fixture
def mock_streamlit():
    with patch("desktop.account_creation.streamlit") as mock_streamlit:
        yield mock_streamlit


@pytest.fixture
def mock_requests():
    with patch("desktop.account_creation.requests") as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_session_state():
    with patch.dict(streamlit.session_state, {"is_otp_sent": False}):
        yield


def test_account_creation_initial_state(mock_streamlit):
    """Test initial state of account creation page"""
    account_creation_page("http://test-api")

    mock_streamlit.title.assert_called_once_with("Create Account with OTP")
    mock_streamlit.write.assert_called_once()
    assert mock_streamlit.text_input.call_count == 2  # Email and Phone inputs


def test_send_otp_success(mock_streamlit, mock_requests):
    """Test successful OTP sending"""
    mock_requests.post.return_value.status_code = 200

    with patch.dict(streamlit.session_state, {"is_otp_sent": False}):
        account_creation_page("http://test-api")

        # Simulate button click with valid email
        mock_streamlit.text_input.return_value = "test@example.com"
        mock_streamlit.button.return_value = True

        assert streamlit.session_state.get("is_otp_sent") == False
        mock_streamlit.success.assert_called_once()


def test_send_otp_failure(mock_streamlit, mock_requests):
    """Test OTP sending failure"""
    mock_requests.post.return_value.status_code = 400
    mock_requests.post.return_value.json.return_value = {"error": "Failed to send OTP"}

    with patch.dict(streamlit.session_state, {"is_otp_sent": False}):
        account_creation_page("http://test-api")

        mock_streamlit.text_input.return_value = "test@example.com"
        mock_streamlit.button.return_value = True

        mock_streamlit.error.assert_called_once()


def test_verify_otp_success(mock_streamlit, mock_requests):
    """Test successful OTP verification"""
    mock_requests.post.return_value.status_code = 201

    with patch.dict(
        streamlit.session_state, {"is_otp_sent": True, "identifier": "test@example.com"}
    ):
        account_creation_page("http://test-api")

        mock_streamlit.text_input.return_value = "123456"
        mock_streamlit.button.return_value = True

        mock_streamlit.success.assert_called_with(
            "Account created successfully! Please log in."
        )


def test_verify_otp_failure(mock_streamlit, mock_requests):
    """Test OTP verification failure"""
    mock_requests.post.return_value.status_code = 400
    mock_requests.post.return_value.json.return_value = {"error": "Invalid OTP"}

    with patch.dict(
        streamlit.session_state, {"is_otp_sent": True, "identifier": "test@example.com"}
    ):
        account_creation_page("http://test-api")

        mock_streamlit.text_input.return_value = "123456"
        mock_streamlit.button.return_value = True

        mock_streamlit.error.assert_called_once()


def test_input_validation(mock_streamlit):
    """Test input validation"""
    account_creation_page("http://test-api")

    # Test empty input
    mock_streamlit.text_input.return_value = ""
    mock_streamlit.button.return_value = True

    mock_streamlit.error.assert_called_with("Please enter either email or phone number")


def test_cancel_operation(mock_streamlit):
    """Test canceling OTP verification"""
    with patch.dict(streamlit.session_state, {"is_otp_sent": True}):
        account_creation_page("http://test-api")

        mock_streamlit.button.return_value = True

        assert streamlit.session_state.get("is_otp_sent") == False
