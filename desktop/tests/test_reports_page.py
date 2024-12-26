import pytest
import streamlit as streamlit
from unittest.mock import Mock, patch, MagicMock
import pandas as pandas
from datetime import datetime
from ..reports_page import reports_page

@pytest.fixture
def mock_streamlit():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.session_state') as mock_session:
        mock_session.user_id = 123
        yield {
            'title': mock_title,
            'markdown': mock_markdown,
            'session': mock_session
        }

@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield {
            'get': mock_get,
            'post': mock_post
        }

def test_reports_page_initialization(mock_streamlit):
    reports_page()
    mock_streamlit['title'].assert_called_once_with("Reports Dashboard")
    mock_streamlit['markdown'].assert_called_with("#### View, Generate, and Manage Reports")

def test_unauthorized_access():
    with patch('streamlit.session_state', {}) as mock_session, \
         patch('streamlit.error') as mock_error:
        reports_page()
        mock_error.assert_called_once_with("Please log in to view reports.")

def test_irs_report_generation_success(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "pdf": b"mock_pdf_data",
        "csv": b"mock_csv_data"
    }
    mock_requests['get'].return_value = mock_response

    with patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.download_button') as mock_download:
        mock_button.return_value = True
        reports_page()
        mock_success.assert_called_once_with("IRS Report generated successfully!")
        assert mock_download.call_count == 2

def test_schedule_c_generation(mock_requests):
    with patch('streamlit.button') as mock_button, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.success') as mock_success:
        mock_button.return_value = True
        reports_page()
        mock_success.assert_called_once_with("IRS Schedule C Report generated successfully!")

def test_custom_report_generation(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"mock_csv_data"
    mock_requests['post'].return_value = mock_response

    with patch('streamlit.date_input') as mock_date, \
         patch('streamlit.text_input') as mock_text, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success:
        mock_date.return_value = datetime.now().date()
        mock_text.return_value = "Test Category"
        mock_button.return_value = True
        
        reports_page()
        mock_success.assert_called_once_with("Custom Report generated successfully!")

def test_gig_platform_connection_display(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "connected_accounts": [
            {"platform": "uber"},
            {"platform": "lyft"}
        ]
    }
    mock_requests['get'].return_value = mock_response

    with patch('streamlit.write') as mock_write:
        reports_page()
        assert mock_write.call_count >= 2

def test_fetch_platform_data(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"trip_id": 1, "amount": 50.0},
            {"trip_id": 2, "amount": 75.0}
        ]
    }
    mock_requests['get'].return_value = mock_response

    with patch('streamlit.selectbox') as mock_select, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.dataframe') as mock_dataframe:
        mock_select.return_value = "Uber"
        mock_button.return_value = True
        
        reports_page()
        mock_success.assert_called_once_with("Fetched data from Uber successfully!")
        mock_dataframe.assert_called_once()

def test_error_handling(mock_requests):
    mock_requests['get'].side_effect = Exception("API Error")

    with patch('streamlit.error') as mock_error:
        reports_page()
        mock_error.assert_called_with("Failed to load connected platforms.")
