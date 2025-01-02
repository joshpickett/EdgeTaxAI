import pytest
from datetime import datetime, timedelta
from ...middleware.auth_middleware import (
    token_required,
    generate_token,
    needs_refresh,
    refresh_token,
    rate_limit,
    APIError,
    SessionManager,
)


def test_generate_token(mock_jwt, sample_user):
    """Test token generation"""
    mock_jwt["encode"].return_value = "dummy_token"
    token = generate_token(sample_user["user_id"])
    assert token == "dummy_token"
    mock_jwt["encode"].assert_called_once()


def test_token_required_missing_token(mock_request_context):
    """Test middleware with missing token"""

    @token_required
    def dummy_route():
        return "Success"

    response = dummy_route()
    assert response[1] == 401
    assert "Token is missing" in response[0].get_json()["error"]


def test_token_required_invalid_token(mock_request_context, mock_jwt):
    """Test middleware with invalid token"""
    mock_request_context.headers = {"Authorization": "Bearer invalid_token"}
    mock_jwt["decode"].side_effect = Exception("Invalid token")

    @token_required
    def dummy_route():
        return "Success"

    response = dummy_route()
    assert response[1] == 401


def test_rate_limit(mock_redis):
    """Test rate limiting decorator"""
    mock_redis.get.return_value = None

    @rate_limit(requests_per_minute=2)
    def dummy_route():
        return "Success"

    # First request should succeed
    response = dummy_route()
    assert "Success" in response

    # Simulate rate limit exceeded
    mock_redis.get.return_value = b"2"
    response = dummy_route()
    assert response[1] == 429


def test_session_manager(mock_redis):
    """Test session management"""
    session_manager = SessionManager()
    device_info = {"device": "test_device", "os": "test_os"}

    # Test session creation
    session_id = session_manager.create_session(1, device_info)
    assert session_id is not None

    # Test session validation
    mock_redis.exists.return_value = True
    mock_redis.get.return_value = b'{"user_id": 1}'
    assert session_manager.validate_session(session_id)


def test_refresh_token(mock_jwt):
    """Test token refresh functionality"""
    old_token = "old_token"
    mock_jwt["decode"].return_value = {
        "user_id": 1,
        "exp": (datetime.utcnow() + timedelta(minutes=4)).timestamp(),
    }

    assert needs_refresh(old_token)

    new_token = refresh_token(old_token)
    assert new_token is not None
