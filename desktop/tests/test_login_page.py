import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from datetime import datetime, timedelta
from desktop.login_page import login_page

@pytest.fixture
def mock_streamlit():
    with patch('desktop.login_page.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('desktop.login_page.requests') as mock_requests:
        yield mock_requests

@pytest.fixture
def mock_keyring():
    with patch('desktop.login_page.keyring') as mock_keyring:
        yield mock_keyring

def test_login_page_initial_state(mock_streamlit):
    """Test initial state of login page"""
    login_page('http://test-api')
    
    mock_streamlit.title.assert_called_once_with("Login")
    mock_streamlit.image.assert_called_once()
    assert mock_streamlit.text_input.call_count == 2  # Identifier and OTP inputs

def test_send_otp_success(mock_streamlit, mock_requests):
    """Test successful OTP sending"""
    mock_requests.post.return_value.status_code = 200
    
    with patch.dict(streamlit.session_state, {'otp_sent': False}):
        login_page('http://test-api')
        
        # Simulate button click
        mock_streamlit.button.return_value = True
        mock_streamlit.text_input.return_value = "test@example.com"
        
        assert streamlit.session_state.get('otp_sent') == False
        mock_streamlit.success.assert_called_once()

def test_login_success(mock_streamlit, mock_requests):
    """Test successful login"""
    mock_requests.post.return_value.status_code = 200
    
    with patch.dict(streamlit.session_state, {'otp_sent': True}):
        login_page('http://test-api')
        
        mock_streamlit.text_input.side_effect = ["test@example.com", "123456"]
        mock_streamlit.button.return_value = True
        
        assert streamlit.session_state.get('authenticated') == True
        mock_streamlit.success.assert_called_with("Login successful!")

def test_biometric_login_success(mock_streamlit, mock_requests, mock_keyring):
    """Test successful biometric login"""
    mock_keyring.get_password.return_value = "stored_token"
    mock_requests.post.return_value.status_code = 200
    
    with patch('platform.system', return_value='Darwin'):
        login_page('http://test-api')
        
        mock_streamlit.button.return_value = True
        
        assert streamlit.session_state.get('authenticated') == True
        mock_streamlit.success.assert_called_with("Login successful!")

def test_session_expiry(mock_streamlit):
    """Test session expiry handling"""
    expired_time = datetime.now() - timedelta(hours=25)
    
    with patch.dict(streamlit.session_state, {'session_expiry': expired_time}):
        login_page('http://test-api')
        
        mock_streamlit.warning.assert_called_with("Session expired. Please log in again.")

def test_remember_me_functionality(mock_streamlit, mock_keyring):
    """Test remember me functionality"""
    login_page('http://test-api')
    
    mock_streamlit.checkbox.return_value = True
    mock_streamlit.text_input.return_value = "test@example.com"
    
    mock_keyring.set_password.assert_called_with("taxedgeai", "last_login", "test@example.com")

def test_login_failure(mock_streamlit, mock_requests):
    """Test login failure"""
    mock_requests.post.return_value.status_code = 401
    
    with patch.dict(streamlit.session_state, {'otp_sent': True}):
        login_page('http://test-api')
        
        mock_streamlit.text_input.side_effect = ["test@example.com", "123456"]
        mock_streamlit.button.return_value = True
        
        assert streamlit.session_state.get('authenticated') != True
        mock_streamlit.error.assert_called()

def test_biometric_login_failure(mock_streamlit, mock_requests, mock_keyring):
    """Test biometric login failure"""
    mock_keyring.get_password.return_value = None
    
    with patch('platform.system', return_value='Darwin'):
        login_page('http://test-api')
        
        mock_streamlit.button.return_value = True
        
        assert streamlit.session_state.get('authenticated') != True
        mock_streamlit.error.assert_called()
