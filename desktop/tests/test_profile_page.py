import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from desktop.profile_page import ProfilePage

@pytest.fixture
def mock_streamlit():
    with patch('desktop.profile_page.streamlit') as mock_st:
        yield mock_st

@pytest.fixture
def mock_requests():
    with patch('desktop.profile_page.requests') as mock_req:
        yield mock_req

@pytest.fixture
def profile_page():
    return ProfilePage()

def test_profile_page_unauthorized(mock_streamlit, profile_page):
    """Test profile page access when unauthorized"""
    streamlit.session_state.clear()
    
    profile_page.profile_page()
    
    mock_streamlit.error.assert_called_once_with("Please log in to view your profile.")

def test_profile_page_fetch_error(mock_streamlit, mock_requests, profile_page):
    """Test profile page when API fetch fails"""
    streamlit.session_state["user_id"] = 1
    mock_requests.get.side_effect = Exception("API Error")
    
    profile_page.profile_page()
    
    mock_streamlit.error.assert_called_with("An error occurred while fetching profile data.")

def test_validate_email(profile_page):
    """Test email validation"""
    assert profile_page.validate_email("test@example.com") is True
    assert profile_page.validate_email("invalid-email") is False

def test_validate_phone(profile_page):
    """Test phone number validation"""
    assert profile_page.validate_phone("+1234567890") is True
    assert profile_page.validate_phone("invalid") is False

def test_render_basic_info_success(mock_streamlit, mock_requests, profile_page):
    """Test successful basic info update"""
    streamlit.session_state["user_id"] = 1
    mock_requests.put.return_value.status_code = 200
    
    with patch.object(profile_page, 'validate_email', return_value=True), \
         patch.object(profile_page, 'validate_phone', return_value=True):
        profile_page.render_basic_info()
        
        mock_streamlit.success.assert_called_with("Profile updated successfully!")

def test_render_tax_documents(mock_streamlit, profile_page):
    """Test tax documents section rendering"""
    profile_page.render_tax_documents()
    
    mock_streamlit.subheader.assert_called_with("Tax Documents")
    assert mock_streamlit.tabs.called

def test_render_security_settings(mock_streamlit, profile_page):
    """Test security settings section rendering"""
    profile_page.render_security_settings()
    
    mock_streamlit.subheader.assert_called_with("Security Settings")

def test_render_gig_platforms(mock_streamlit, profile_page):
    """Test gig platforms section rendering"""
    profile_page.render_gig_platforms()
    
    mock_streamlit.subheader.assert_called_with("Gig Platform Management")

def test_upload_tax_documents(mock_streamlit, profile_page):
    """Test tax document upload functionality"""
    mock_file = Mock()
    mock_file.name = "test.pdf"
    mock_streamlit.file_uploader.return_value = mock_file
    
    profile_page.upload_tax_documents()
    
    assert mock_streamlit.file_uploader.called
