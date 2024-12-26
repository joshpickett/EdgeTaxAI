import pytest
import requests
from unittest.mock import Mock, patch
from ..utils import handle_api_response, send_post_request, send_get_request, validate_input_fields
from ..token_storage import TokenStorage
import os
import json
from cryptography.fernet import Fernet

@pytest.fixture
def test_secret_key():
    return Fernet.generate_key().decode()

@pytest.fixture
def token_storage(test_secret_key, tmp_path):
    with patch('os.path.expanduser') as mock_expanduser:
        mock_expanduser.return_value = str(tmp_path)
        return TokenStorage(test_secret_key)

@pytest.fixture
def sample_token_data():
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600
    }

def test_token_storage_initialization(token_storage, tmp_path):
    storage_path = os.path.join(tmp_path, '.taxedgeai', 'tokens')
    assert os.path.exists(storage_path)

def test_store_token_success(token_storage, sample_token_data):
    result = token_storage.store_token(123, "uber", sample_token_data)
    assert result == True
    
    # Verify file exists
    filename = token_storage._get_token_file(123, "uber")
    assert os.path.exists(filename)

def test_get_token_success(token_storage, sample_token_data):
    # Store token first
    token_storage.store_token(123, "uber", sample_token_data)
    
    # Retrieve token
    retrieved_data = token_storage.get_token(123, "uber")
    assert retrieved_data == sample_token_data

def test_get_nonexistent_token(token_storage):
    result = token_storage.get_token(999, "nonexistent")
    assert result is None

def test_delete_token_success(token_storage, sample_token_data):
    # Store token first
    token_storage.store_token(123, "uber", sample_token_data)
    
    # Delete token
    result = token_storage.delete_token(123, "uber")
    assert result == True
    
    # Verify file no longer exists
    filename = token_storage._get_token_file(123, "uber")
    assert not os.path.exists(filename)

def test_delete_nonexistent_token(token_storage):
    result = token_storage.delete_token(999, "nonexistent")
    assert result == True  # Should return True even if file didn't exist

def test_encryption_decryption(token_storage, sample_token_data):
    # Store encrypted token
    token_storage.store_token(123, "uber", sample_token_data)
    
    # Read raw encrypted data
    filename = token_storage._get_token_file(123, "uber")
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    
    # Verify data is actually encrypted
    assert encrypted_data != json.dumps(sample_token_data).encode()
    
    # Verify decryption works
    decrypted_data = token_storage.get_token(123, "uber")
    assert decrypted_data == sample_token_data

def test_error_handling(token_storage, sample_token_data):
    with patch('builtins.open', side_effect=Exception("Test error")):
        result = token_storage.store_token(123, "uber", sample_token_data)
        assert result == False

def test_file_path_generation(token_storage):
    filename = token_storage._get_token_file(123, "uber")
    assert "123_uber_token.enc" in filename

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"data": "test"}
    return mock

def test_handle_api_response_success(mock_response):
    result = handle_api_response(mock_response)
    assert result == {"data": "test"}

def test_handle_api_response_error():
    mock_error_response = Mock()
    mock_error_response.status_code = 400
    mock_error_response.json.return_value = {"error": "Bad Request"}
    
    result = handle_api_response(mock_error_response)
    assert result is None

def test_send_post_request_success(mock_response):
    with patch('requests.post', return_value=mock_response):
        result = send_post_request("http://test.com", {"test": "data"})
        assert result == {"data": "test"}

def test_send_post_request_with_headers(mock_response):
    with patch('requests.post', return_value=mock_response) as mock_post:
        custom_headers = {"Authorization": "Bearer test"}
        send_post_request("http://test.com", {"test": "data"}, custom_headers)
        
        called_headers = mock_post.call_args[1]['headers']
        assert called_headers["Authorization"] == "Bearer test"
        assert called_headers["Content-Type"] == "application/json"

def test_send_get_request_success(mock_response):
    with patch('requests.get', return_value=mock_response):
        result = send_get_request("http://test.com")
        assert result == {"data": "test"}

def test_send_get_request_network_error():
    with patch('requests.get', side_effect=requests.exceptions.RequestException):
        result = send_get_request("http://test.com")
        assert result is None

def test_validate_input_fields_success():
    fields = {
        "name": "Test User",
        "email": "test@example.com"
    }
    assert validate_input_fields(fields) == True

def test_validate_input_fields_failure():
    fields = {
        "name": "Test User",
        "email": ""
    }
    assert validate_input_fields(fields) == False

def test_api_error_logging():
    with patch('logging.error') as mock_logging:
        mock_error_response = Mock()
        mock_error_response.status_code = 500
        mock_error_response.json.return_value = {"error": "Server Error"}
        
        handle_api_response(mock_error_response)
        mock_logging.assert_called_once()
