import pytest
import os
import json
from unittest.mock import Mock, patch, mock_open
from cryptography.fernet import Fernet
from desktop.token_storage import TokenStorage

@pytest.fixture
def token_storage():
    """Create a TokenStorage instance with a test key"""
    test_key = Fernet.generate_key()
    return TokenStorage(test_key.decode())

@pytest.fixture
def sample_token_data():
    """Sample token data for testing"""
    return {
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'expires_in': 3600
    }

def test_store_token_success(token_storage, sample_token_data):
    """Test successful token storage"""
    with patch('builtins.open', mock_open()) as mock_file:
        result = token_storage.store_token(1, 'uber', sample_token_data)
        
        assert result is True
        mock_file.assert_called_once()
        # Verify encrypted data was written
        written_data = mock_file().write.call_args[0][0]
        assert isinstance(written_data, bytes)

def test_store_token_failure(token_storage, sample_token_data):
    """Test token storage failure"""
    with patch('builtins.open', side_effect=Exception("Storage error")):
        result = token_storage.store_token(1, 'uber', sample_token_data)
        
        assert result is False

def test_get_token_success(token_storage, sample_token_data):
    """Test successful token retrieval"""
    # First store the token
    encrypted_data = token_storage.fernet.encrypt(
        json.dumps(sample_token_data).encode()
    )
    
    with patch('builtins.open', mock_open(read_data=encrypted_data)):
        with patch('os.path.exists', return_value=True):
            result = token_storage.get_token(1, 'uber')
            
            assert result == sample_token_data

def test_get_token_not_found(token_storage):
    """Test token retrieval when file doesn't exist"""
    with patch('os.path.exists', return_value=False):
        result = token_storage.get_token(1, 'uber')
        
        assert result is None

def test_get_token_decrypt_error(token_storage):
    """Test token retrieval with decryption error"""
    with patch('builtins.open', mock_open(read_data=b'invalid_data')):
        with patch('os.path.exists', return_value=True):
            result = token_storage.get_token(1, 'uber')
            
            assert result is None

def test_delete_token_success(token_storage):
    """Test successful token deletion"""
    with patch('os.path.exists', return_value=True):
        with patch('os.remove') as mock_remove:
            result = token_storage.delete_token(1, 'uber')
            
            assert result is True
            mock_remove.assert_called_once()

def test_delete_token_not_found(token_storage):
    """Test token deletion when file doesn't exist"""
    with patch('os.path.exists', return_value=False):
        result = token_storage.delete_token(1, 'uber')
        
        assert result is True  # Should return True even if file doesn't exist

def test_delete_token_error(token_storage):
    """Test token deletion error"""
    with patch('os.path.exists', return_value=True):
        with patch('os.remove', side_effect=Exception("Deletion error")):
            result = token_storage.delete_token(1, 'uber')
            
            assert result is False

def test_token_file_path(token_storage):
    """Test token file path generation"""
    file_path = token_storage._get_token_file(1, 'uber')
    
    assert '1_uber_token.enc' in file_path
    assert '.taxedgeai/tokens' in file_path

def test_storage_directory_creation(token_storage):
    """Test storage directory creation"""
    with patch('os.makedirs') as mock_makedirs:
        TokenStorage('test_key')
        
        mock_makedirs.assert_called_once()
        assert mock_makedirs.call_args[1]['exist_ok'] is True
