import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import requests
from desktop.gig_platform_service import (
    get_oauth_link, fetch_connected_platforms, fetch_platform_data,
    refresh_platform_token, get_sync_status, validate_platform_connection,
    disconnect_platform, handle_oauth_callback, GigPlatformError
)

@pytest.fixture
def mock_requests():
    with patch('desktop.gig_platform_service.requests') as mock_req:
        yield mock_req

@pytest.fixture
def mock_token_storage():
    with patch('desktop.gig_platform_service.token_storage') as mock_storage:
        yield mock_storage

def test_get_oauth_link_success(mock_requests):
    """Test successful OAuth link generation"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {'oauth_url': 'test_url'}
    
    result = get_oauth_link('uber', 'http://callback')
    
    assert result == 'test_url'
    mock_requests.get.assert_called_once()

def test_get_oauth_link_failure(mock_requests):
    """Test OAuth link generation failure"""
    mock_requests.get.return_value.status_code = 400
    
    result = get_oauth_link('uber', 'http://callback')
    
    assert result is None

def test_fetch_connected_platforms_success(mock_requests):
    """Test successful platform connection fetch"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'connected_accounts': ['uber', 'lyft']
    }
    
    result = fetch_connected_platforms(1)
    
    assert len(result) == 2
    assert 'uber' in result

def test_fetch_platform_data_success(mock_requests):
    """Test successful platform data fetch"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'trips': [{'id': 1}]
    }
    
    result = fetch_platform_data(1, 'uber')
    
    assert 'trips' in result
    assert len(result['trips']) == 1

def test_refresh_platform_token_success(mock_requests):
    """Test successful token refresh"""
    mock_requests.post.return_value.status_code = 200
    
    result = refresh_platform_token(1, 'uber')
    
    assert result is True

def test_get_sync_status_success(mock_requests):
    """Test successful sync status retrieval"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'status': 'completed',
        'last_sync': '2023-01-01T00:00:00Z'
    }
    
    result = get_sync_status(1, 'uber')
    
    assert result['status'] == 'completed'
    assert 'last_sync' in result

def test_validate_platform_connection_success(mock_requests):
    """Test successful platform connection validation"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'connected': True,
        'last_sync': '2023-01-01T00:00:00Z'
    }
    
    result = validate_platform_connection(1, 'uber')
    
    assert result.connected is True
    assert result.last_sync is not None

def test_disconnect_platform_success(mock_requests):
    """Test successful platform disconnection"""
    mock_requests.post.return_value.status_code = 200
    
    result = disconnect_platform(1, 'uber')
    
    assert result is True

def test_handle_oauth_callback_success(mock_requests, mock_token_storage):
    """Test successful OAuth callback handling"""
    mock_requests.post.return_value.status_code = 200
    mock_requests.post.return_value.json.return_value = {
        'token_data': {'access_token': 'test_token'}
    }
    mock_token_storage.store_token.return_value = True
    
    result = handle_oauth_callback('test_code', 'uber', 1)
    
    assert result is True

def test_error_handling(mock_requests):
    """Test error handling in platform operations"""
    mock_requests.get.side_effect = requests.exceptions.RequestException
    
    result = get_oauth_link('uber', 'http://callback')
    
    assert result is None

def test_retry_mechanism(mock_requests):
    """Test retry mechanism for failed requests"""
    mock_requests.get.side_effect = [
        requests.exceptions.RequestException,
        requests.exceptions.RequestException,
        Mock(status_code=200, json=lambda: {'oauth_url': 'test_url'})
    ]
    
    result = get_oauth_link('uber', 'http://callback')
    
    assert result == 'test_url'
    assert mock_requests.get.call_count == 3
