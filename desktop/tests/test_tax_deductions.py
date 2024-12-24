import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
import pandas as pandas
from desktop.tax_deductions import tax_deductions_page

@pytest.fixture
def mock_streamlit():
    with patch('desktop.tax_deductions.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('desktop.tax_deductions.requests') as mock_requests:
        yield mock_requests

@pytest.fixture
def sample_expenses():
    return pandas.DataFrame([
        {'description': 'Gas', 'amount': 50.0},
        {'description': 'Office supplies', 'amount': 100.0}
    ])

def test_tax_deductions_unauthorized(mock_streamlit):
    """Test tax deductions page when user is not logged in"""
    with patch.dict(streamlit.session_state, clear=True):
        tax_deductions_page()
        mock_streamlit.error.assert_called_once_with("Please log in to view tax deductions.")

def test_process_uploaded_file(mock_streamlit, mock_requests, sample_expenses):
    """Test processing uploaded expense file"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_streamlit.file_uploader.return_value = Mock(
            read=lambda: sample_expenses.to_csv().encode()
        )
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.json.return_value = {
            'suggestions': [{'category': 'Business', 'amount': 150.0}]
        }
        
        tax_deductions_page()
        
        mock_streamlit.dataframe.assert_called_once()

def test_manual_expense_input(mock_streamlit, mock_requests):
    """Test manual expense input processing"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_streamlit.text_input.return_value = "Office rent"
        mock_streamlit.number_input.return_value = 1000.0
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.json.return_value = {
            'suggestions': [{'category': 'Business', 'amount': 1000.0}]
        }
        
        tax_deductions_page()
        
        mock_streamlit.dataframe.assert_called_once()

def test_api_error_handling(mock_streamlit, mock_requests, sample_expenses):
    """Test API error handling"""
    with patch.dict(streamlit.session_state, {'user_id': '123'}):
        mock_streamlit.file_uploader.return_value = Mock(
            read=lambda: sample_expenses.to_csv().encode()
        )
        mock_requests.post.side_effect = Exception("API Error")
        
        tax_deductions_page()
        
        mock_streamlit.error.assert_called()
