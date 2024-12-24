import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from desktop.main import main, check_auth

@pytest.fixture
def mock_streamlit():
    with patch('desktop.main.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_session_state():
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        yield

def test_check_auth_logged_in(mock_streamlit, mock_session_state):
    """Test authentication check when user is logged in"""
    check_auth()
    mock_streamlit.warning.assert_not_called()
    mock_streamlit.stop.assert_not_called()

def test_check_auth_not_logged_in(mock_streamlit):
    """Test authentication check when user is not logged in"""
    with patch.dict(streamlit.session_state, clear=True):
        check_auth()
        mock_streamlit.warning.assert_called_once()
        mock_streamlit.stop.assert_called_once()

def test_main_navigation(mock_streamlit, mock_session_state):
    """Test main navigation functionality"""
    mock_streamlit.sidebar.radio.return_value = "Dashboard"
    
    main()
    
    mock_streamlit.title.assert_called_with("Welcome to EdgeTaxAI")
    mock_streamlit.subheader.assert_called_with("Dashboard")

def test_main_logout(mock_streamlit, mock_session_state):
    """Test logout functionality"""
    mock_streamlit.sidebar.radio.return_value = "Logout"
    
    main()
    
    assert mock_streamlit.session_state.clear.called
    mock_streamlit.success.assert_called_with("Logged out successfully!")
    mock_streamlit.experimental_rerun.assert_called_once()

@patch('desktop.main.bank_integration_page')
def test_bank_integration_navigation(mock_bank_integration, mock_streamlit, mock_session_state):
    """Test bank integration page navigation"""
    mock_streamlit.sidebar.radio.return_value = "Bank Integration"
    
    main()
    
    mock_bank_integration.assert_called_once()

def test_gig_platforms_navigation(mock_streamlit, mock_session_state):
    """Test gig platforms page navigation"""
    mock_streamlit.sidebar.radio.return_value = "Gig Platforms"
    
    main()
    
    mock_streamlit.subheader.assert_called_with("Gig Platform Integration")

@patch('desktop.main.get_oauth_link')
def test_platform_connection(mock_get_oauth, mock_streamlit, mock_session_state):
    """Test platform connection functionality"""
    mock_streamlit.sidebar.radio.return_value = "Gig Platforms"
    mock_get_oauth.return_value = "https://oauth-url"
    
    main()
    
    assert mock_get_oauth.called

def test_reports_navigation(mock_streamlit, mock_session_state):
    """Test reports page navigation"""
    mock_streamlit.sidebar.radio.return_value = "Reports"
    
    main()
    
    mock_streamlit.subheader.assert_called_with("Reports")

def test_tax_optimization_navigation(mock_streamlit, mock_session_state):
    """Test tax optimization page navigation"""
    mock_streamlit.sidebar.radio.return_value = "Tax Optimization"
    
    main()
    
    mock_streamlit.subheader.assert_called_with("Tax Optimization")

def test_oauth_callback_handling(mock_streamlit, mock_session_state):
    """Test OAuth callback handling"""
    mock_streamlit.sidebar.radio.return_value = "Gig Platforms"
    mock_streamlit.experimental_get_query_params.return_value = {
        'code': ['test_code'],
        'platform': ['uber']
    }
    
    with patch('desktop.main.handle_oauth_callback', return_value=True) as mock_handle:
        main()
        
        mock_handle.assert_called_once_with(
            code='test_code',
            platform='uber',
            user_id='123'
        )
