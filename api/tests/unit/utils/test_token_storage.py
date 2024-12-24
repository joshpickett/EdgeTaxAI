import pytest
from unittest.mock import Mock, patch
import jwt
from datetime import datetime, timedelta
from api.utils.token_storage import TokenStorage

@pytest.fixture
def token_storage():
    return TokenStorage('test_secret_key')

@pytest.fixture
def sample_claims():
    return {
        'user_id': 1,
        'role': 'user',
        'platform': 'uber'
    }

def test_generate_token_success(token_storage, sample_claims):
    """Test successful token generation"""
    token = token_storage.generate_token(1, sample_claims)
    
    decoded = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
    assert decoded['user_id'] == 1
    assert decoded['role'] == 'user'
    assert decoded['platform'] == 'uber'
    assert 'exp' in decoded
    assert 'iat' in decoded

def test_generate_token_expiry(token_storage):
    """Test token expiration time"""
    token = token_storage.generate_token(1)
    decoded = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
    
    exp_time = datetime.fromtimestamp(decoded['exp'])
    iat_time = datetime.fromtimestamp(decoded['iat'])
    
    assert (exp_time - iat_time).total_seconds() == 24 * 3600  # 24 hours

def test_store_token_success(token_storage):
    """Test successful token storage"""
    with patch('keyring.set_password') as mock_set:
        result = token_storage.store_token(1, 'test_token')
        
        assert result is True
        mock_set.assert_called_once_with('taxedgeai', 'user_1', 'test_token')

def test_store_token_failure(token_storage):
    """Test token storage failure"""
    with patch('keyring.set_password', side_effect=Exception("Storage error")):
        result = token_storage.store_token(1, 'test_token')
        
        assert result is False

def test_retrieve_token_success(token_storage):
    """Test successful token retrieval"""
    with patch('keyring.get_password', return_value='test_token'):
        token = token_storage.retrieve_token(1)
        
        assert token == 'test_token'

def test_retrieve_token_not_found(token_storage):
    """Test token retrieval when not found"""
    with patch('keyring.get_password', return_value=None):
        token = token_storage.retrieve_token(1)
        
        assert token is None

def test_verify_token_valid(token_storage):
    """Test verification of valid token"""
    token = token_storage.generate_token(1)
    is_valid, claims = token_storage.verify_token(token)
    
    assert is_valid is True
    assert claims['user_id'] == 1

def test_verify_token_expired(token_storage):
    """Test verification of expired token"""
    with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
        is_valid, claims = token_storage.verify_token('expired_token')
        
        assert is_valid is False
        assert claims['error'] == 'Token expired'

def test_verify_token_invalid(token_storage):
    """Test verification of invalid token"""
    with patch('jwt.decode', side_effect=jwt.InvalidTokenError):
        is_valid, claims = token_storage.verify_token('invalid_token')
        
        assert is_valid is False
        assert claims['error'] == 'Invalid token'
