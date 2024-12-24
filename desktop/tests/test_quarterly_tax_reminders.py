import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from datetime import datetime
from desktop.quarterly_tax_reminders import quarterly_tax_reminders_page

@pytest.fixture
def mock_streamlit():
    with patch('desktop.quarterly_tax_reminders.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('desktop.quarterly_tax_reminders.requests') as mock_requests:
        yield mock_requests

def test_unauthorized_access(mock_streamlit):
    """Test unauthorized access handling"""
    with patch.dict(streamlit.session_state, clear=True):
        quarterly_tax_reminders_page()
        mock_streamlit.error.assert_called_once_with("Please log in to set tax reminders.")

def test_schedule_reminder_success(mock_streamlit, mock_requests):
    """Test successful reminder scheduling"""
    # Mock session state
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        # Mock user inputs
        mock_streamlit.text_input.return_value = "+1234567890"
        mock_streamlit.date_input.return_value = datetime.now().date()
        mock_streamlit.button.return_value = True
        
        # Mock API response
        mock_requests.post.return_value.status_code = 200
        
        quarterly_tax_reminders_page()
        
        mock_streamlit.success.assert_called_once_with("Reminder scheduled successfully!")

def test_schedule_reminder_missing_fields(mock_streamlit, mock_requests):
    """Test reminder scheduling with missing fields"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_streamlit.text_input.return_value = ""
        mock_streamlit.date_input.return_value = None
        mock_streamlit.button.return_value = True
        
        quarterly_tax_reminders_page()
        
        mock_streamlit.error.assert_called_with("Both phone number and reminder date are required.")

def test_schedule_reminder_api_error(mock_streamlit, mock_requests):
    """Test reminder scheduling with API error"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_streamlit.text_input.return_value = "+1234567890"
        mock_streamlit.date_input.return_value = datetime.now().date()
        mock_streamlit.button.return_value = True
        
        # Mock API error
        mock_requests.post.return_value.status_code = 500
        mock_requests.post.return_value.json.return_value = {"error": "API Error"}
        
        quarterly_tax_reminders_page()
        
        mock_streamlit.error.assert_called_once()

def test_schedule_reminder_exception(mock_streamlit, mock_requests):
    """Test reminder scheduling with exception"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_streamlit.text_input.return_value = "+1234567890"
        mock_streamlit.date_input.return_value = datetime.now().date()
        mock_streamlit.button.return_value = True
        
        # Mock exception
        mock_requests.post.side_effect = Exception("Connection error")
        
        quarterly_tax_reminders_page()
        
        mock_streamlit.error.assert_called_with(
            "An unexpected error occurred while scheduling the reminder."
        )

def test_page_layout(mock_streamlit):
    """Test page layout and components"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        quarterly_tax_reminders_page()
        
        mock_streamlit.title.assert_called_once_with("Quarterly Tax Reminders")
        mock_streamlit.image.assert_called_once()
        mock_streamlit.markdown.assert_called_once_with(
            "#### Schedule SMS reminders for your quarterly tax payments."
        )
