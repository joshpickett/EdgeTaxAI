import pytest
import streamlit as streamlit
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from ..login_page import login_page, handle_login


@pytest.fixture
def mock_auth_service():
    return Mock()


@pytest.fixture
def mock_streamlit():
    with patch("streamlit.title") as mock_title, patch(
        "streamlit.image"
    ) as mock_image, patch("streamlit.session_state") as mock_session:
        mock_session.otp_sent = False
        mock_session.authenticated = False
        yield {"title": mock_title, "image": mock_image, "session": mock_session}


def test_login_page_initialization(mock_streamlit):
    login_page("http://test-api")
    mock_streamlit["title"].assert_called_once_with("Login")
    mock_streamlit["image"].assert_called_once()


def test_handle_login_success(mock_auth_service):
    mock_auth_service.login.return_value = Mock(token="test_token")

    with patch("streamlit.session_state") as mock_session:
        result = handle_login("test@email.com", "123456", mock_auth_service)
        assert result == True
        assert mock_session.authenticated == True
        assert isinstance(mock_session.session_expiry, datetime)


def test_handle_login_failure(mock_auth_service):
    mock_auth_service.login.side_effect = Exception("Login failed")

    with patch("streamlit.error") as mock_error:
        result = handle_login("test@email.com", "wrong_otp", mock_auth_service)
        assert result == False
        mock_error.assert_called_once()


def test_session_expiry_check():
    with patch("streamlit.session_state") as mock_session, patch(
        "streamlit.warning"
    ) as mock_warning:
        mock_session.session_expiry = datetime.now() - timedelta(hours=25)
        login_page("http://test-api")
        mock_warning.assert_called_once_with("Session expired. Please log in again")


def test_remember_me_functionality():
    with patch("keyring.set_password") as mock_keyring, patch(
        "streamlit.checkbox"
    ) as mock_checkbox:
        mock_checkbox.return_value = True
        login_page("http://test-api")
        mock_keyring.assert_called_once()
