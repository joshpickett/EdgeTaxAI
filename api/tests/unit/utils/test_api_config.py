import pytest
from unittest.mock import patch, Mock
import os
from api.utils.api_config import APIConfig


def test_plaid_host_sandbox():
    """Test Plaid host retrieval for sandbox environment"""
    with patch.dict(os.environ, {"PLAID_ENV": "sandbox"}):
        host = APIConfig.get_plaid_host()
        assert host == "https://sandbox.plaid.com"


def test_plaid_host_development():
    """Test Plaid host retrieval for development environment"""
    with patch.dict(os.environ, {"PLAID_ENV": "development"}):
        host = APIConfig.get_plaid_host()
        assert host == "https://development.plaid.com"


def test_plaid_host_production():
    """Test Plaid host retrieval for production environment"""
    with patch.dict(os.environ, {"PLAID_ENV": "production"}):
        host = APIConfig.get_plaid_host()
        assert host == "https://api.plaid.com"


def test_plaid_host_invalid_env():
    """Test Plaid host retrieval with invalid environment"""
    with patch.dict(os.environ, {"PLAID_ENV": "invalid"}):
        host = APIConfig.get_plaid_host()
        assert host == "https://sandbox.plaid.com"  # Should default to sandbox


def test_plaid_host_missing_env():
    """Test Plaid host retrieval with missing environment variable"""
    with patch.dict(os.environ, clear=True):
        host = APIConfig.get_plaid_host()
        assert host == "https://sandbox.plaid.com"  # Should default to sandbox


def test_logging_configuration():
    """Test logging configuration"""
    with patch("logging.error") as mock_logging:
        APIConfig.get_plaid_host()
        mock_logging.assert_not_called()


def test_error_handling():
    """Test error handling in config retrieval"""
    with patch.dict(os.environ, {"PLAID_ENV": None}):
        host = APIConfig.get_plaid_host()
        assert host == "https://sandbox.plaid.com"  # Should handle None gracefully
