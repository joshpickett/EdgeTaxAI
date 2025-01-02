import pytest
from flask import json
from api.routes.auth_routes import auth_blueprint
from api.utils.token_manager import TokenManager
from api.utils.session_manager import SessionManager

# ...rest of the code...


def test_verify_otp(client):
    response = client.post(
        "/api/auth/verify-otp", json={"email": "test@example.com", "otp_code": "123456"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "refresh_token" in data
    assert TokenManager.verify_token(data["access_token"])


# ...rest of the code...


def test_successful_login(self, client):
    response = client.post("/api/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "refresh_token" in data
    assert SessionManager.validate_session(data["access_token"])
