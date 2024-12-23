import pytest
from api.utils.error_handler import ErrorHandler, APIError
from unittest.mock import Mock, patch

@pytest.fixture
def error_handler():
    return ErrorHandler()

def test_handle_api_error():
    """Test handling of API errors"""
    error_handler = ErrorHandler()
    error = APIError("Test error", status_code=400)
    
    response = error_handler.handle_error(error)
    
    assert response['error'] == "Test error"
    assert response['status_code'] == 400
    assert 'timestamp' in response

def test_handle_validation_error():
    """Test handling of validation errors"""
    error_handler = ErrorHandler()
    error = ValueError("Invalid input")
    
    response = error_handler.handle_error(error)
    
    assert response['error'] == "Invalid input"
    assert response['status_code'] == 400
    assert 'timestamp' in response

def test_handle_database_error():
    """Test handling of database errors"""
    error_handler = ErrorHandler()
    error = Exception("Database connection failed")
    
    response = error_handler.handle_error(error)
    
    assert 'Database error' in response['error']
    assert response['status_code'] == 500
    assert 'timestamp' in response

def test_handle_unknown_error():
    """Test handling of unknown errors"""
    error_handler = ErrorHandler()
    error = Exception("Unknown error")
    
    response = error_handler.handle_error(error)
    
    assert response['error'] == "Internal server error"
    assert response['status_code'] == 500
    assert 'timestamp' in response

def test_log_error():
    """Test error logging functionality"""
    error_handler = ErrorHandler()
    
    with patch('logging.error') as mock_logger:
        error = ValueError("Test error")
        error_handler.handle_error(error)
        
        mock_logger.assert_called_once()

def test_custom_error_handling():
    """Test custom error handling"""
    error_handler = ErrorHandler()
    
    @error_handler.custom_handler(KeyError)
    def handle_key_error(error):
        return {"error": "Key not found", "status_code": 404}
    
    response = error_handler.handle_error(KeyError("test"))
    
    assert response['error'] == "Key not found"
    assert response['status_code'] == 404

def test_error_formatting():
    """Test error response formatting"""
    error_handler = ErrorHandler()
    error = APIError("Test error", status_code=400)
    
    response = error_handler.format_error_response(error)
    
    assert isinstance(response, dict)
    assert 'error' in response
    assert 'status_code' in response
    assert 'timestamp' in response

def test_error_chain_handling():
    """Test handling of chained errors"""
    error_handler = ErrorHandler()
    
    try:
        try:
            raise ValueError("Original error")
        except ValueError as e:
            raise APIError("Wrapped error", status_code=400) from e
    except APIError as e:
        response = error_handler.handle_error(e)
    
    assert response['error'] == "Wrapped error"
    assert response['status_code'] == 400
    assert 'original_error' in response

def test_batch_error_handling():
    """Test handling multiple errors"""
    error_handler = ErrorHandler()
    errors = [
        ValueError("Error 1"),
        KeyError("Error 2"),
        APIError("Error 3", status_code=400)
    ]
    
    responses = error_handler.handle_multiple_errors(errors)
    
    assert len(responses) == 3
    assert all('error' in response for response in responses)
    assert all('status_code' in response for response in responses)
