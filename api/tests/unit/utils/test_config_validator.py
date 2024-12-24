import pytest
from unittest.mock import patch, Mock
from api.utils.config_validator import validate_config, get_database_url, get_api_key, ConfigurationError

@pytest.fixture
def mock_config():
    return {
        'SECRET_KEY': 'test_key',
        'DATABASE_URL': 'sqlite:///test.db',
        'PLAID_CLIENT_ID': 'test_plaid_id',
        'PLAID_SECRET': 'test_plaid_secret',
        'TWILIO_ACCOUNT_SID': 'test_twilio_sid',
        'TWILIO_AUTH_TOKEN': 'test_twilio_token',
        'REDIS_URL': 'redis://localhost',
        'SENTRY_DSN': 'test_sentry_dsn',
        'AWS_ACCESS_KEY': 'test_aws_key',
        'AWS_SECRET_KEY': 'test_aws_secret'
    }

def test_validate_config_success(mock_config):
    """Test successful configuration validation"""
    validate_config(mock_config)  # Should not raise any exception

def test_validate_config_missing_settings(mock_config):
    """Test validation with missing required settings"""
    del mock_config['SECRET_KEY']
    with pytest.raises(ConfigurationError):
        validate_config(mock_config)

def test_validate_config_production_settings():
    """Test validation of production-specific settings"""
    with patch('os.getenv', return_value='production'):
        config = {'SENTRY_DSN': None, 'AWS_ACCESS_KEY': None}
        with pytest.raises(ConfigurationError):
            validate_config(config)

def test_get_database_url_success():
    """Test successful database URL retrieval"""
    with patch('os.getenv', return_value='postgresql://localhost/db'):
        url = get_database_url()
        assert url == 'postgresql://localhost/db'

def test_get_database_url_default():
    """Test default database URL"""
    with patch('os.getenv', return_value=None):
        url = get_database_url()
        assert url == 'sqlite:///database.db'

def test_get_api_key_success():
    """Test successful API key retrieval"""
    with patch('os.getenv', return_value='test_key'):
        key = get_api_key('TEST_SERVICE')
        assert key == 'test_key'

def test_get_api_key_missing():
    """Test missing API key handling"""
    with patch('os.getenv', return_value=None):
        key = get_api_key('TEST_SERVICE')
        assert key is None

def test_validate_database_config():
    """Test database configuration validation"""
    config = {
        'DATABASE_URL': 'sqlite:///test.db',
        'DATABASE_POOL_SIZE': 5,
        'DATABASE_MAX_OVERFLOW': 10
    }
    assert validate_database_config(config) is True

def test_validate_database_config_missing():
    """Test database configuration with missing settings"""
    config = {'DATABASE_URL': 'sqlite:///test.db'}
    assert validate_database_config(config) is False

def test_load_custom_config():
    """Test loading custom configuration"""
    with patch('builtins.open', mock_open(read_data='{"TEST_KEY": "test_value"}')):
        result = load_custom_config('test_config.json')
        assert result.get('TEST_KEY') == 'test_value'
