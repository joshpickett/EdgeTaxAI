import pytest
from unittest.mock import patch, Mock
from flask import Flask, json
from ..routes.auth_routes import auth_blueprint
from ..utils.otp_manager import OTPManager
from ..utils.token_storage import TokenStorage

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(auth_blueprint)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

class TestAuthRoutes:
    @pytest.fixture
    def mock_otp_manager(self):
        with patch('api.routes.auth_routes.OTPManager') as mock:
            yield mock

    @pytest.fixture
    def mock_token_storage(self):
        with patch('api.routes.auth_routes.TokenStorage') as mock:
            yield mock

    def test_signup_success(self, client, mock_otp_manager):
        data = {
            'email': 'test@example.com',
            'phone_number': '+1234567890'
        }
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 201
        assert b'OTP sent for verification' in response.data

    def test_signup_invalid_email(self, client):
        data = {
            'email': 'invalid_email',
            'phone_number': '+1234567890'
        }
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert b'Invalid email format' in response.data

    def test_verify_otp_success(self, client, mock_otp_manager):
        data = {
            'email': 'test@example.com',
            'otp_code': '123456'
        }
        mock_otp_manager.verify_otp_for_user.return_value = True
        
        response = client.post(
            '/api/auth/verify-otp',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert b'OTP verified successfully' in response.data

    def test_verify_otp_invalid(self, client, mock_otp_manager):
        data = {
            'email': 'test@example.com',
            'otp_code': '123456'
        }
        mock_otp_manager.verify_otp_for_user.return_value = False
        
        response = client.post(
            '/api/auth/verify-otp',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 401
        assert b'Invalid or expired OTP' in response.data

    def test_login_success(self, client, mock_otp_manager):
        data = {
            'email': 'test@example.com'
        }
        response = client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert b'OTP sent' in response.data

    def test_login_user_not_found(self, client):
        data = {
            'email': 'nonexistent@example.com'
        }
        response = client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 404
        assert b'User not found' in response.data

    def test_biometric_register_success(self, client):
        data = {
            'user_id': 123,
            'biometric_data': 'sample_biometric_data'
        }
        response = client.post(
            '/api/auth/biometric/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert b'Biometric authentication registered successfully' in response.data

    def test_biometric_register_missing_data(self, client):
        data = {
            'user_id': 123
        }
        response = client.post(
            '/api/auth/biometric/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert b'Missing required data' in response.data

    @patch('api.routes.auth_routes.check_login_attempts')
    def test_login_rate_limit(self, mock_check_attempts, client):
        mock_check_attempts.return_value = False
        data = {
            'email': 'test@example.com'
        }
        response = client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 429
        assert b'Too many login attempts' in response.data
