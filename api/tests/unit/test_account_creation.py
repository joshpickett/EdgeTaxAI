import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from api.account_creation import account_creation_page

@pytest.fixture
def mock_streamlit():
    with patch('api.account_creation.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('api.account_creation.requests') as mock_requests:
        yield mock_requests

def test_account_creation_success(mock_streamlit, mock_requests):
    """Test successful account creation"""
    # Mock user input
    mock_streamlit.text_input.side_effect = [
        "John Doe",  # full_name
        "john@example.com",  # email
        "+1234567890",  # phone_number
        "password123"  # password
    ]
    
    # Mock successful API response
    mock_response = Mock()
    mock_response.status_code = 201
    mock_requests.post.return_value = mock_response
    
    # Call the function
    account_creation_page("http://test-api")
    
    # Verify API call
    mock_requests.post.assert_called_once_with(
        "http://test-api/auth/signup",
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "password": "password123"
        }
    )
    
    # Verify success message
    mock_streamlit.success.assert_called_once()

def test_account_creation_missing_fields(mock_streamlit, mock_requests):
    """Test account creation with missing fields"""
    # Mock incomplete user input
    mock_streamlit.text_input.side_effect = [
        "John Doe",
        "",  # Missing email
        "+1234567890",
        "password123"
    ]
    
    # Call the function
    account_creation_page("http://test-api")
    
    # Verify error message
    mock_streamlit.error.assert_called_with("All fields are required.")
    # Verify no API call was made
    mock_requests.post.assert_not_called()

def test_account_creation_api_error(mock_streamlit, mock_requests):
    """Test account creation with API error"""
    # Mock user input
    mock_streamlit.text_input.side_effect = [
        "John Doe",
        "john@example.com",
        "+1234567890",
        "password123"
    ]
    
    # Mock failed API response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Email already exists"}
    mock_requests.post.return_value = mock_response
    
    # Call the function
    account_creation_page("http://test-api")
    
    # Verify error message
    mock_streamlit.error.assert_called_once()
