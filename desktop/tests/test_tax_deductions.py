import pytest
import streamlit as streamlit
from unittest.mock import Mock, patch, MagicMock
import pandas as pandas
from ..tax_deductions import tax_deductions_page

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

def test_tax_deductions_page_initialization(mock_streamlit):
    tax_deductions_page()
    mock_streamlit['title'].assert_called_once_with("AI-Flagged Tax Deductions")
    mock_streamlit['markdown'].assert_called_with("#### Optimize your expenses with AI-detected deductions.")

def test_unauthorized_access():
    with patch('streamlit.session_state', {}) as mock_session, \
         patch('streamlit.error') as mock_error:
        tax_deductions_page()
        mock_error.assert_called_once_with("Please log in to view tax deductions.")

def test_file_upload_processing(mock_requests):
    mock_file = Mock()
    mock_file.read.return_value = b"description,amount\nOffice supplies,100.50"
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suggestions": [
            {"description": "Office supplies", "amount": 100.50, "category": "Office Expenses"}
        ]
    }
    mock_requests.return_value = mock_response

    with patch('streamlit.file_uploader') as mock_uploader, \
         patch('streamlit.dataframe') as mock_dataframe:
        mock_uploader.return_value = mock_file
        
        tax_deductions_page()
        mock_dataframe.assert_called_once()

def test_manual_input_processing(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suggestions": [
            {"description": "Computer", "amount": 1000.00, "category": "Equipment"}
        ]
    }
    mock_requests.return_value = mock_response

    with patch('streamlit.text_input') as mock_text, \
         patch('streamlit.number_input') as mock_number, \
         patch('streamlit.dataframe') as mock_dataframe:
        mock_text.return_value = "Computer"
        mock_number.return_value = 1000.00
        
        tax_deductions_page()
        mock_dataframe.assert_called_once()

def test_api_error_handling(mock_requests):
    mock_requests.side_effect = Exception("API Error")

    with patch('streamlit.error') as mock_error, \
         patch('streamlit.text_input') as mock_text, \
         patch('streamlit.number_input') as mock_number:
        mock_text.return_value = "Test expense"
        mock_number.return_value = 100.00
        
        tax_deductions_page()
        mock_error.assert_called_with("An error occurred while fetching tax deductions: API Error")

def test_empty_suggestions_handling(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"suggestions": []}
    mock_requests.return_value = mock_response

    with patch('streamlit.info') as mock_info, \
         patch('streamlit.text_input') as mock_text, \
         patch('streamlit.number_input') as mock_number:
        mock_text.return_value = "Test expense"
        mock_number.return_value = 100.00
        
        tax_deductions_page()
        mock_info.assert_called_with("No tax-deductible expenses detected.")
