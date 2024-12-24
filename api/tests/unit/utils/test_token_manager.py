import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
from api.utils.token_manager import TokenManager

@pytest.fixture
def token_manager():
    return TokenManager()

@pytest.fixture
def mock_redis():
    with patch('redis.from_url') as mock:
        yield mock.return_value

@pytest.fixture
def sample_token_data():
    return {
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'expires_in': 3600
    }

def test_check_token_expiry_needs_refresh(token_manager, mock_redis):
    """Test token expiry check when refresh is needed"""
    expiry_time = (datetime.now() - timedelta(minutes=5)).isoformat()
    mock_redis.get.return_value = json.dumps({'expires_at': expiry_time})
    
    result = token_manager.check_token_expiry(1, 'uber')
    
    assert result is True
    mock_redis.get.assert_called_once_with('tokens:1:uber')

def test_check_token_expiry_valid(token_manager, mock_redis):
    """Test token expiry check when token is still valid"""
    expiry_time = (datetime.now() + timedelta(hours=1)).isoformat()
    mock_redis.get.return_value = json.dumps({'expires_at': expiry_time})
    
    result = token_manager.check_token_expiry(1, 'uber')
    
    assert result is False

def test_check_token_expiry_no_token(token_manager, mock_redis):
    """Test token expiry check when no token exists"""
    mock_redis.get.return_value = None
    
    result = token_manager.check_token_expiry(1, 'uber')
    
    assert result is True

def test_refresh_token_success(token_manager, mock_redis, sample_token_data):
    """Test successful token refresh"""
    result = token_manager.refresh_token(1, 'uber', sample_token_data)
    
    assert result is True
    mock_redis.setex.assert_called_once()

def test_refresh_token_failure(token_manager, mock_redis, sample_token_data):
    """Test token refresh failure"""
    mock_redis.setex.side_effect = Exception("Redis error")
    
    result = token_manager.refresh_token(1, 'uber', sample_token_data)
    
    assert result is False

def test_refresh_token_expiry_calculation(token_manager, mock_redis, sample_token_data):
    """Test token expiry time calculation during refresh"""
    token_manager.refresh_token(1, 'uber', sample_token_data)
    
    call_args = mock_redis.setex.call_args[0]
    stored_data = json.loads(call_args[2])
    
    assert 'expires_at' in stored_data
    expires_at = datetime.fromisoformat(stored_data['expires_at'])
    assert (expires_at - datetime.now()).total_seconds() == pytest.approx(3600, rel=1)

def test_refresh_token_data_structure(token_manager, mock_redis, sample_token_data):
    """Test structure of stored token data"""
    token_manager.refresh_token(1, 'uber', sample_token_data)
    
    call_args = mock_redis.setex.call_args[0]
    stored_data = json.loads(call_args[2])
    
    assert 'access_token' in stored_data
    assert 'refresh_token' in stored_data
    assert 'refreshed_at' in stored_data
    assert 'expires_at' in stored_data

def test_refresh_token_custom_expiry(token_manager, mock_redis):
    """Test token refresh with custom expiry time"""
    custom_token_data = {
        'access_token': 'test_token',
        'expires_in': 7200  # 2 hours
    }
    
    token_manager.refresh_token(1, 'uber', custom_token_data)
    
    call_args = mock_redis.setex.call_args[0]
    assert call_args[1].total_seconds() == 7200
