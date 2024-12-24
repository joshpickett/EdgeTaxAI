import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from api.utils.token_storage import TokenStorage

@pytest.fixture
def token_storage():
    return TokenStorage('test_secret_key')

@pytest.fixture
def mock_keyring():
    with patch('keyring.set_password') as mock_set:
        with patch('keyring.get_password') as mock_get:
            yield {
                'set': mock_set,
                'get': mock_get
            }

def test_generate_token_success(token_storage):
    # Test token generation with valid inputs
    user_id = 123
    token = token_storage.generate_token(user_id)
    
    # Verify token can be decoded
    decoded = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
    assert decoded['user_id'] == user_id
    assert 'exp' in decoded
    assert 'iat' in decoded

def test_generate_token_with_claims(token_storage):
    # Test token generation with additional claims
    user_id = 123
    additional_claims = {'role': 'admin', 'platform': 'mobile'}
    token = token_storage.generate_token(user_id, additional_claims)
    
    decoded = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
    assert decoded['user_id'] == user_id
    assert decoded['role'] == 'admin'
    assert decoded['platform'] == 'mobile'

def test_store_token_success(token_storage, mock_keyring):
    # Test storing token successfully
    user_id = 123
    token = "test_token"
    
    result = token_storage.store_token(user_id, token)
    
    assert result is True
    mock_keyring['set'].assert_called_once_with(
        'taxedgeai', 
        token_storage._get_storage_key(user_id), 
        token
    )

def test_retrieve_token_success(token_storage, mock_keyring):
    # Test retrieving stored token
    user_id = 123
    expected_token = "test_token"
    mock_keyring['get'].return_value = expected_token
    
    retrieved_token = token_storage.retrieve_token(user_id)
    
    assert retrieved_token == expected_token
    mock_keyring['get'].assert_called_once_with(
        'taxedgeai', 
        token_storage._get_storage_key(user_id)
    )

def test_verify_token_valid(token_storage):
    # Test verifying a valid token
    user_id = 123
    token = token_storage.generate_token(user_id)
    
    is_valid, claims = token_storage.verify_token(token)
    
    assert is_valid is True
    assert claims['user_id'] == user_id

def test_verify_token_expired(token_storage):
    # Test verifying an expired token
    user_id = 123
    expired_date = datetime.utcnow() - timedelta(hours=25)
    
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = expired_date
        token = token_storage.generate_token(user_id)
    
    is_valid, claims = token_storage.verify_token(token)
    
    assert is_valid is False
    assert claims['error'] == 'Token expired'

def test_verify_token_invalid(token_storage):
    # Test verifying an invalid token
    invalid_token = "invalid.token.string"
    
    is_valid, claims = token_storage.verify_token(invalid_token)
    
    assert is_valid is False
    assert claims['error'] == 'Invalid token'

def test_storage_key_generation(token_storage):
    # Test storage key generation
    user_id = 123
    expected_key = 'user_123_access_token'
    
    key = token_storage._get_storage_key(user_id)
    
    assert key == expected_key

def test_error_handling(token_storage, mock_keyring):
    # Test error handling during storage operations
    mock_keyring['set'].side_effect = Exception("Storage error")
    
    result = token_storage.store_token(123, "test_token")
    
    assert result is False
