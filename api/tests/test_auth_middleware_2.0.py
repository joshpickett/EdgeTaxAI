import pytest
import jwt
from datetime import datetime, timedelta
import os
from unittest.mock import Mock, patch
from flask import Flask, request
from ..middleware.auth_middleware import (
    token_required, 
    validate_token_format,
    generate_token, 
    needs_refresh,
    refresh_token,
    rate_limit,
    AuthError,
    SessionManager
)

@pytest.fixture(autouse=True)
def setup_environment():
    os.environ['JWT_SECRET_KEY'] = 'your-secret-key'
    yield
    del os.environ['JWT_SECRET_KEY']

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.app_context():
        yield app

class TestAuthMiddleware:
    def test_token_required_valid_token(self, app):
        with app.test_request_context():
            # Create a valid token
            token = generate_token(123)
            request.headers = {'Authorization': f'Bearer {token}'}
            
            @token_required
            def test_endpoint():
                return {'success': True}
            
            response = test_endpoint()
            assert response.get('success') is True

    def test_token_required_missing_token(self, app):
        with app.test_request_context():
            request.headers = {}
            
            @token_required
            def test_endpoint():
                return {'success': True}
            
            with pytest.raises(AuthError) as exc:
                test_endpoint()
            assert str(exc.value) == "Token is missing"

    def test_token_required_invalid_token(self, app):
        with app.test_request_context():
            request.headers = {'Authorization': 'Bearer invalid_token'}
            
            @token_required
            def test_endpoint():
                return {'success': True}
            
            with pytest.raises(AuthError) as exc:
                test_endpoint()
            assert str(exc.value) == "Invalid token format"

    def test_token_required_malformed_token(self, app):
        with app.test_request_context():
            request.headers = {'Authorization': 'Bearer abc.def'}
            
            @token_required
            def test_endpoint():
                return {'success': True}
            
            with pytest.raises(AuthError) as exc:
                test_endpoint()
            assert str(exc.value) == "Invalid token format"

    def test_generate_token(self):
        user_id = 123
        token = generate_token(user_id)
        decoded = jwt.decode(token, key='your-secret-key', algorithms=['HS256'])
        assert decoded['user_id'] == user_id

    def test_needs_refresh_true(self):
        # Create token that expires in 4 minutes
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=4),
            'user_id': 123
        }
        token = jwt.encode(payload, key='your-secret-key', algorithm='HS256')
        assert needs_refresh(token) is True

    def test_needs_refresh_false(self):
        # Create token that expires in 6 hours
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=6),
            'user_id': 123
        }
        token = jwt.encode(payload, key='your-secret-key', algorithm='HS256')
        assert needs_refresh(token) is False

    def test_validate_token_format(self):
        # Valid token format
        assert validate_token_format("header.payload.signature") is True
        
        # Invalid token formats
        assert validate_token_format("header.payload") is False
        assert validate_token_format("header") is False
        assert validate_token_format("") is False
        assert validate_token_format("header.payload.signature.extra") is False

    def test_refresh_token_success(self):
        # Create expired token
        payload = {
            'exp': datetime.utcnow() - timedelta(minutes=5),
            'user_id': 123
        }
        old_token = jwt.encode(payload, key='your-secret-key', algorithm='HS256')
        new_token = refresh_token(old_token)
        assert new_token is not None
        assert new_token != old_token

    @patch('redis.Redis')
    def test_rate_limit_not_exceeded(self, mock_redis):
        mock_redis.return_value.get.return_value = None
        
        @rate_limit(requests_per_minute=5)
        def test_endpoint():
            return {'success': True}
            
        with app.test_request_context():
            response = test_endpoint()
            assert response.get('success') is True

    @patch('redis.Redis')
    def test_rate_limit_exceeded(self, mock_redis):
        mock_redis.return_value.get.return_value = b'5'
        mock_redis.return_value.ttl.return_value = 30
        
        @rate_limit(requests_per_minute=5)
        def test_endpoint():
            return {'success': True}
            
        with app.test_request_context():
            response = test_endpoint()
            assert response.status_code == 429

class TestSessionManager:
    @pytest.fixture
    def session_manager(self):
        return SessionManager()

    def test_create_session(self, session_manager):
        user_id = 123
        device_info = {'device': 'iPhone', 'os': 'iOS 15'}
        session_id = session_manager.create_session(user_id, device_info)
        assert session_id is not None

    def test_validate_session_valid(self, session_manager):
        user_id = 123
        device_info = {'device': 'iPhone', 'os': 'iOS 15'}
        session_id = session_manager.create_session(user_id, device_info)
        assert session_manager.validate_session(session_id) is True

    def test_validate_session_invalid(self, session_manager):
        assert session_manager.validate_session('invalid_session_id') is False

    def test_concurrent_sessions(self, session_manager):
        user_id = 123
        device_info1 = {'device': 'iPhone', 'os': 'iOS 15'}
        device_info2 = {'device': 'Android', 'os': 'Android 12'}
        
        session1 = session_manager.create_session(user_id, device_info1)
        session2 = session_manager.create_session(user_id, device_info2)
        
        assert session1 != session2
        assert session_manager.validate_session(session1)
        assert session_manager.validate_session(session2)

    @patch('redis.Redis')
    def test_redis_connection_failure(self, mock_redis):
        mock_redis.side_effect = redis.RedisError
        
        @rate_limit(requests_per_minute=5)
        def test_endpoint():
            return {'success': True}
            
        with app.test_request_context():
            response = test_endpoint()
            assert response.status_code == 500
