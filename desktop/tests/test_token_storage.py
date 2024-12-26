import pytest
import os
import json
from unittest.mock import Mock, patch
from cryptography.fernet import Fernet
from ..token_storage import TokenStorage

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
