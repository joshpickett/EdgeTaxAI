import pytest
import redis
import sqlite3
import os
from unittest.mock import Mock, patch
from ...middleware.auth_middleware import redis_client

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    mock_redis = Mock(spec=redis.Redis)
    with patch('api.middleware.auth_middleware.redis_client', mock_redis):
        yield mock_redis

@pytest.fixture
def test_db():
    """Create test database connection"""
    db_path = "test_database.db"
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def mock_jwt():
    """Mock JSON Web Token functions"""
    with patch('jwt.encode') as mock_encode, \
         patch('jwt.decode') as mock_decode:
        yield {
            'encode': mock_encode,
            'decode': mock_decode
        }

@pytest.fixture
def mock_request_context():
    """Mock Flask request context"""
    with patch('flask.request') as mock_request:
        mock_request.headers = {}
        mock_request.remote_addr = '127.0.0.1'
        yield mock_request

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        'user_id': 1,
        'email': 'test@example.com',
        'phone_number': '+1234567890'
    }
