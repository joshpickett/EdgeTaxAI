import pytest
from flask import Flask, json
from unittest.mock import patch, Mock
from ...routes.auth_routes import auth_bp
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_signup_success(client, mock_redis):
    """Test successful user signup"""
    data = {
        "email": "test@example.com",
        "phone_number": "+1234567890"
    }
    
    with patch('api.routes.auth_routes.send_sms') as mock_send_sms:
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(data),
            content_type='application/json'
        )
        
    assert response.status_code == 201
    assert b"Signup successful" in response.data
    mock_send_sms.assert_called_once()

def test_signup_invalid_email(client):
    """Test signup with invalid email"""
    data = {
        "email": "invalid-email",
        "phone_number": "+1234567890"
    }
    
    response = client.post(
        '/api/auth/signup',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert b"Invalid email format" in response.data

def test_verify_otp_success(client, test_db):
    """Test successful OTP verification"""
    # Setup test user with OTP
    with test_db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (email, otp_code, otp_expiry) VALUES (?, ?, ?)",
            ("test@example.com", "123456", 
             (datetime.now() + timedelta(minutes=5)).isoformat())
        )
        test_db.commit()
    
    data = {
        "email": "test@example.com",
        "otp_code": "123456"
    }
    
    response = client.post(
        '/api/auth/verify-otp',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert b"OTP verified successfully" in response.data

def test_verify_otp_expired(client, test_db):
    """Test expired OTP verification"""
    # Setup test user with expired OTP
    with test_db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (email, otp_code, otp_expiry) VALUES (?, ?, ?)",
            ("test@example.com", "123456", 
             (datetime.now() - timedelta(minutes=10)).isoformat())
        )
        test_db.commit()
    
    data = {
        "email": "test@example.com",
        "otp_code": "123456"
    }
    
    response = client.post(
        '/api/auth/verify-otp',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    assert b"Invalid or expired OTP" in response.data

def test_login_success(client, mock_redis):
    """Test successful login attempt"""
    data = {
        "email": "test@example.com",
        "phone_number": "+1234567890"
    }
    
    with patch('api.routes.auth_routes.send_sms') as mock_send_sms:
        response = client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
    
    assert response.status_code == 200
    assert b"OTP sent" in response.data
    mock_send_sms.assert_called_once()

def test_login_rate_limit(client, mock_redis):
    """Test login rate limiting"""
    mock_redis.get.return_value = b"6"  # Simulate rate limit exceeded
    
    data = {
        "email": "test@example.com"
    }
    
    response = client.post(
        '/api/auth/login',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 429
    assert b"Too many login attempts" in response.data

def test_biometric_register_success(client):
    """Test successful biometric registration"""
    data = {
        "user_id": 1,
        "biometric_data": "test_biometric_data"
    }
    
    with patch('api.routes.auth_routes.biometric_auth.register_biometric') as mock_register:
        mock_register.return_value = True
        response = client.post(
            '/api/auth/biometric/register',
            data=json.dumps(data),
            content_type='application/json'
        )
    
    assert response.status_code == 200
    assert b"registered successfully" in response.data
