import pytest
from unittest.mock import Mock, patch
import requests
from desktop.utils import (
    handle_api_response,
    send_post_request,
    send_get_request,
    validate_input_fields
)

@pytest.fixture
def mock_response():
    """Create a mock response object"""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {'data': 'test'}
    return mock

def test_handle_api_response_success(mock_response):
    """Test successful API response handling"""
    result = handle_api_response(mock_response)
    
    assert result == {'data': 'test'}
    mock_response.json.assert_called_once()

def test_handle_api_response_error(mock_response):
    """Test API response handling with error"""
    mock_response.status_code = 400
    mock_response.json.return_value = {'error': 'Bad request'}
    
    result = handle_api_response(mock_response)
    
    assert result is None

def test_handle_api_response_exception():
    """Test API response handling with exception"""
    mock_response = Mock()
    mock_response.json.side_effect = Exception("JSON decode error")
    
    result = handle_api_response(mock_response)
    
    assert result is None

@patch('requests.post')
def test_send_post_request_success(mock_post, mock_response):
    """Test successful POST request"""
    mock_post.return_value = mock_response
    
    result = send_post_request('http://test.com', {'data': 'test'})
    
    assert result == {'data': 'test'}
    mock_post.assert_called_once()

@patch('requests.post')
def test_send_post_request_with_headers(mock_post, mock_response):
    """Test POST request with custom headers"""
    mock_post.return_value = mock_response
    custom_headers = {'Authorization': 'Bearer token'}
    
    send_post_request('http://test.com', {'data': 'test'}, custom_headers)
    
    called_headers = mock_post.call_args[1]['headers']
    assert called_headers['Authorization'] == 'Bearer token'
    assert called_headers['Content-Type'] == 'application/json'

@patch('requests.post')
def test_send_post_request_error(mock_post):
    """Test POST request with network error"""
    mock_post.side_effect = requests.exceptions.RequestException("Network error")
    
    result = send_post_request('http://test.com', {'data': 'test'})
    
    assert result is None

@patch('requests.get')
def test_send_get_request_success(mock_get, mock_response):
    """Test successful GET request"""
    mock_get.return_value = mock_response
    
    result = send_get_request('http://test.com')
    
    assert result == {'data': 'test'}
    mock_get.assert_called_once()

@patch('requests.get')
def test_send_get_request_with_headers(mock_get, mock_response):
    """Test GET request with custom headers"""
    mock_get.return_value = mock_response
    custom_headers = {'Authorization': 'Bearer token'}
    
    send_get_request('http://test.com', custom_headers)
    
    called_headers = mock_get.call_args[1]['headers']
    assert called_headers['Authorization'] == 'Bearer token'
    assert called_headers['Content-Type'] == 'application/json'

@patch('requests.get')
def test_send_get_request_error(mock_get):
    """Test GET request with network error"""
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    
    result = send_get_request('http://test.com')
    
    assert result is None

def test_validate_input_fields_success():
    """Test input validation with valid fields"""
    fields = {
        'name': 'John',
        'email': 'john@example.com'
    }
    
    result = validate_input_fields(fields)
    
    assert result is True

def test_validate_input_fields_empty():
    """Test input validation with empty fields"""
    fields = {
        'name': '',
        'email': 'john@example.com'
    }
    
    result = validate_input_fields(fields)
    
    assert result is False

def test_validate_input_fields_none():
    """Test input validation with None values"""
    fields = {
        'name': None,
        'email': 'john@example.com'
    }
    
    result = validate_input_fields(fields)
    
    assert result is False
