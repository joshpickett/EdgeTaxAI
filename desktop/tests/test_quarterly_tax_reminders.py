import pytest
import streamlit as streamlit
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ..quarterly_tax_reminders import quarterly_tax_reminders_page

@pytest.fixture
def mock_streamlit():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.image') as mock_image, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.session_state') as mock_session:
        mock_session.user_id = 123
        yield {
            'title': mock_title,
            'image': mock_image,
            'markdown': mock_markdown,
            'session': mock_session
        }

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post:
        yield mock_post

def test_quarterly_tax_reminders_page_initialization(mock_streamlit):
    quarterly_tax_reminders_page()
    mock_streamlit['title'].assert_called_once_with("Quarterly Tax Reminders")
    mock_streamlit['markdown'].assert_called_with("#### Schedule SMS reminders for your quarterly tax payments.")

def test_unauthorized_access(mock_streamlit):
    with patch('streamlit.session_state') as mock_session, \
         patch('streamlit.error') as mock_error:
        mock_session.get.return_value = None
        quarterly_tax_reminders_page()
        mock_error.assert_called_once_with("Please log in to set tax reminders.")

def test_successful_reminder_scheduling(mock_streamlit, mock_requests):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.date_input') as mock_date, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success:
        
        mock_input.return_value = "+1234567890"
        mock_date.return_value = datetime.now().date()
        mock_button.return_value = True
        mock_requests.return_value.status_code = 200
        
        quarterly_tax_reminders_page()
        mock_success.assert_called_once_with("Reminder scheduled successfully!")

def test_missing_fields_validation(mock_streamlit):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.date_input') as mock_date, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.error') as mock_error:
        
        mock_input.return_value = ""
        mock_date.return_value = None
        mock_button.return_value = True
        
        quarterly_tax_reminders_page()
        mock_error.assert_called_once_with("Both phone number and reminder date are required.")

def test_api_error_handling(mock_streamlit, mock_requests):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.date_input') as mock_date, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.error') as mock_error:
        
        mock_input.return_value = "+1234567890"
        mock_date.return_value = datetime.now().date()
        mock_button.return_value = True
        mock_requests.return_value.status_code = 500
        mock_requests.return_value.json.return_value = {"error": "API Error"}
        
        quarterly_tax_reminders_page()
        mock_error.assert_called_once_with("API Error")

def test_exception_handling(mock_streamlit, mock_requests):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.date_input') as mock_date, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.error') as mock_error:
        
        mock_input.return_value = "+1234567890"
        mock_date.return_value = datetime.now().date()
        mock_button.return_value = True
        mock_requests.side_effect = Exception("Network Error")
        
        quarterly_tax_reminders_page()
        mock_error.assert_called_once_with("An unexpected error occurred while scheduling the reminder.")
