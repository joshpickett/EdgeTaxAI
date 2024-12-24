import pytest
from unittest.mock import Mock, patch
import os
import hashlib
from ..utils.biometric_auth import BiometricAuthentication

class TestBiometricAuthentication:
    @pytest.fixture
    def biometric_authentication(self):
        return BiometricAuthentication()

    @pytest.fixture
    def mock_database(self):
        with patch('sqlite3.connect') as mock:
            yield mock

    def test_register_biometric_success(self, biometric_authentication, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        
        result = biometric_authentication.register_biometric(123, "sample_biometric_data")
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()

    def test_verify_biometric_success(self, biometric_authentication, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        
        # Mock stored hash and salt
        stored_salt = os.urandom(32)
        stored_hash = hashlib.pbkdf2_hmac(
            'sha256',
            "sample_biometric_data".encode(),
            stored_salt,
            100000
        ).hex()
        
        mock_cursor.fetchone.return_value = (stored_hash, stored_salt)
        
        result = biometric_authentication.verify_biometric(123, "sample_biometric_data")
        assert result is True

    def test_verify_biometric_failure(self, biometric_authentication, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = biometric_authentication.verify_biometric(123, "wrong_biometric_data")
        assert result is False

    def test_verify_hardware_support(self, biometric_authentication, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        result = biometric_authentication.verify_hardware_support()
        assert result is True

    def test_hash_biometric(self, biometric_authentication):
        salt = os.urandom(32)
        hashed_data = biometric_authentication._hash_biometric("sample_data", salt)
        
        assert isinstance(hashed_data, str)
        assert len(hashed_data) > 0

    def test_register_biometric_invalid_data(self, biometric_authentication):
        with pytest.raises(ValueError):
            biometric_authentication.register_biometric(123, "")

    def test_verify_biometric_invalid_user(self, biometric_authentication, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = biometric_authentication.verify_biometric(999, "sample_biometric_data")
        assert result is False

    def test_hash_collision_resistance(self, biometric_authentication):
        salt = os.urandom(32)
        hash1 = biometric_authentication._hash_biometric("data1", salt)
        hash2 = biometric_authentication._hash_biometric("data2", salt)
        
        assert hash1 != hash2

    def test_salt_uniqueness(self, biometric_authentication):
        salt1 = os.urandom(32)
        salt2 = os.urandom(32)
        
        assert salt1 != salt2
        
        hash1 = biometric_authentication._hash_biometric("same_data", salt1)
        hash2 = biometric_authentication._hash_biometric("same_data", salt2)
        
        assert hash1 != hash2
