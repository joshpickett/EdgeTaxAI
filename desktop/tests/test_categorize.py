import pytest
from unittest.mock import patch
from desktop.categorize import categorize_expense

@pytest.fixture
def mock_requests():
    with patch('desktop.categorize.requests') as mock_request:
        yield mock_request

def test_categorize_expense_success(mock_requests):
    """Test successful expense categorization"""
    mock_requests.post.return_value.status_code = 200
    mock_requests.post.return_value.json.return_value = {"category": "Food"}
    
    result = categorize_expense("http://test-api", "lunch at restaurant")
    
    assert result == "Food"
    mock_requests.post.assert_called_once()

def test_categorize_expense_failure(mock_requests):
    """Test failed expense categorization"""
    mock_requests.post.return_value.status_code = 500
    
    result = categorize_expense("http://test-api", "lunch")
    
    assert result == "Uncategorized"

def test_categorize_expense_empty_description():
    """Test categorization with empty description"""
    result = categorize_expense("http://test-api", "")
    
    assert result == "Invalid_Input"

def test_categorize_expense_api_error(mock_requests):
    """Test categorization with API error"""
    mock_requests.post.side_effect = Exception("API Error")
    
    result = categorize_expense("http://test-api", "lunch")
    
    assert result == "Error"

def test_categorize_expense_none_description():
    """Test categorization with None description"""
    result = categorize_expense("http://test-api", None)
    
    assert result == "Invalid_Input"
