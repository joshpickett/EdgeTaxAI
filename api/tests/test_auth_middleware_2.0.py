import os
import pytest
from flask import Flask, request
from ..middleware.auth_middleware import (
    token_required, 
    validate_token_format,
    generate_token, 
    needs_refresh,
    refresh_token,
    rate_limit
)

@pytest.fixture(autouse=True)
def setup_environment():
    os.environ['JWT_SECRET_KEY'] = 'your-secret-key'
    yield
    del os.environ['JWT_SECRET_KEY']

def test_invalid_token_format():
    @token_required
    def test_endpoint():
        return {'success': True}

    with pytest.raises(AuthError) as exc:
        test_endpoint()
    assert str(exc.value) == "Invalid token format"

def test_validate_token_format():
    # Valid token format
    assert validate_token_format("header.payload.signature") is True
    
    # Invalid token formats
    assert validate_token_format("header.payload") is False
    assert validate_token_format("header") is False
    assert validate_token_format("") is False
    assert validate_token_format("header.payload.signature.extra") is False

def test_rate_limit_exceeded():
    @patch('redis.Redis')
    def test_rate_limit_exceeded(self, mock_redis):
        mock_redis.return_value.get.return_value = b'5'
        mock_redis.return_value.ttl.return_value = 30
        @rate_limit(requests_per_minute=5)
        def test_endpoint():
            return {'success': True}
