import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from flask import Flask, request
from ..middleware.auth_middleware import (
    token_required, 
    generate_token, 
    needs_refresh,
    refresh_token,
    rate_limit,
    AuthError,
    SessionManager
)

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def mock_token_manager():
    with patch('api.middleware.auth_middleware.TokenManager') as mock:
        yield mock

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
            assert str(exc.value) == "Invalid token"

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
