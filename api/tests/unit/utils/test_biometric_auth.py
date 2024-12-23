import pytest
from unittest.mock import Mock, patch
import os
from api.utils.biometric_auth import BiometricAuthentication

@pytest.fixture
def mock_database():
    return Mock()

@pytest.fixture
def biometric_auth(mock_database):
    with patch('api.utils.biometric_auth.get_database_connection', return_value=mock_database):
        return BiometricAuthentication()

def test_register_biometric_success(biometric_auth, mock_database):
    """Test successful biometric registration"""
    mock_cursor = Mock()
    mock_database.cursor.return_value = mock_cursor
    
    result = biometric_auth.register_biometric(
        user_id=1,
        biometric_data="sample_biometric_data"
    )
    
    assert result is True
    mock_cursor.execute.assert_called_once()
    mock_database.commit.assert_called_once()

def test_register_biometric_failure(biometric_auth, mock_database):
    """Test biometric registration failure"""
    mock_database.cursor.side_effect = Exception("Database error")
    
    result = biometric_auth.register_biometric(
        user_id=1,
        biometric_data="sample_biometric_data"
    )
    
    assert result is False

def test_verify_biometric_success(biometric_auth, mock_database):
    """Test successful biometric verification"""
    mock_cursor = Mock()
    # Simulate stored hash and salt
    mock_cursor.fetchone.return_value = (
        "stored_hash",
        os.urandom(32)  # Random salt
    )
    mock_database.cursor.return_value = mock_cursor
    
    with patch.object(biometric_auth, '_hash_biometric', 
                     return_value="stored_hash"):
        result = biometric_auth.verify_biometric(
            user_id=1,
            biometric_data="sample_biometric_data"
        )
        
        assert result is True

def test_verify_biometric_failure(biometric_auth, mock_database):
    """Test biometric verification failure"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = None
    mock_database.cursor.return_value = mock_cursor
    
    result = biometric_auth.verify_biometric(
        user_id=1,
        biometric_data="sample_biometric_data"
    )
    
    assert result is False

def test_verify_biometric_invalid_hash(biometric_auth, mock_database):
    """Test biometric verification with invalid hash"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (
        "stored_hash",
        os.urandom(32)
    )
    mock_database.cursor.return_value = mock_cursor
    
    with patch.object(biometric_auth, '_hash_biometric', 
                     return_value="different_hash"):
        result = biometric_auth.verify_biometric(
            user_id=1,
            biometric_data="sample_biometric_data"
        )
        
        assert result is False

def test_hash_biometric(biometric_auth):
    """Test biometric data hashing"""
    salt = os.urandom(32)
    biometric_data = "sample_biometric_data"
    
    hash1 = biometric_auth._hash_biometric(biometric_data, salt)
    hash2 = biometric_auth._hash_biometric(biometric_data, salt)
    
    assert hash1 == hash2  # Same input should produce same hash
    assert isinstance(hash1, str)
    assert len(hash1) > 0

def test_verify_hardware_support_success(biometric_auth, mock_database):
    """Test successful hardware support verification"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (1,)  # Table exists
    mock_database.cursor.return_value = mock_cursor
    
    result = biometric_auth.verify_hardware_support()
    
    assert result is True

def test_verify_hardware_support_failure(biometric_auth, mock_database):
    """Test hardware support verification failure"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (0,)  # Table doesn't exist
    mock_database.cursor.return_value = mock_cursor
    
    result = biometric_auth.verify_hardware_support()
    
    assert result is False

def test_verify_hardware_support_error(biometric_auth, mock_database):
    """Test hardware support verification error handling"""
    mock_database.cursor.side_effect = Exception("Database error")
    
    result = biometric_auth.verify_hardware_support()
    
    assert result is False
