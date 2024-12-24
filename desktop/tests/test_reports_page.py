import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from datetime import datetime
from desktop.reports_page import reports_page

@pytest.fixture
def mock_streamlit():
    with patch('desktop.reports_page.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('desktop.reports_page.requests') as mock_requests:
        yield mock_requests

def test_reports_page_unauthorized(mock_streamlit):
    """Test reports page when user is not logged in"""
    with patch.dict(streamlit.session_state, clear=True):
        reports_page()
        mock_streamlit.error.assert_called_once_with("Please log in to view reports.")

def test_generate_irs_report_success(mock_streamlit, mock_requests):
    """Test successful IRS report generation"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.json.return_value = {
            'pdf': b'pdf_content',
            'csv': b'csv_content'
        }
        
        reports_page()
        
        mock_streamlit.success.assert_called_with("IRS Report generated successfully!")
        assert mock_streamlit.download_button.call_count == 2

def test_generate_schedule_c_success(mock_streamlit, mock_requests):
    """Test successful Schedule C report generation"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_requests.get.return_value.status_code = 200
        
        reports_page()
        
        mock_streamlit.success.assert_called_with("IRS Schedule C Report generated successfully!")

def test_generate_custom_report_success(mock_streamlit, mock_requests):
    """Test successful custom report generation"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.content = b'report_content'
        
        reports_page()
        
        mock_streamlit.success.assert_called_with("Custom Report generated successfully!")

def test_fetch_platform_data_success(mock_streamlit, mock_requests):
    """Test successful platform data fetching"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.json.return_value = {'data': []}
        
        reports_page()
        
        mock_streamlit.success.assert_called_with("Fetched data from Uber successfully!")

def test_error_handling(mock_streamlit, mock_requests):
    """Test error handling in reports page"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_requests.get.side_effect = Exception("API Error")
        
        reports_page()
        
        mock_streamlit.error.assert_called()
