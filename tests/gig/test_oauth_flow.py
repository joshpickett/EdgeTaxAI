import pytest
from unittest.mock import patch, MagicMock
from api.routes.gig_routes import exchange_token, refresh_token
from api.utils.gig_utils import OAUTH_CONFIG

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post:
        yield mock_post

def test_exchange_token_success(mock_requests):
    """Test successful token exchange"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token"
    }
    mock_requests.return_value = mock_response
    
    response = exchange_token("uber", "test_code")
    
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_exchange_token_failure(mock_requests):
    """Test failed token exchange"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "invalid_code"}
    mock_requests.return_value = mock_response
    
    response = exchange_token("uber", "invalid_code")
    
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_refresh_token_success(mock_requests):
    """Test successful token refresh"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token"
    }
    mock_requests.return_value = mock_response
    
    response = refresh_token("uber", "test_refresh_token")
    
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_refresh_token_failure(mock_requests):
    """Test failed token refresh"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "invalid_refresh_token"}
    mock_requests.return_value = mock_response
    
    response = refresh_token("uber", "invalid_refresh_token")
    
    assert response.status_code == 400
    assert "error" in response.get_json()
