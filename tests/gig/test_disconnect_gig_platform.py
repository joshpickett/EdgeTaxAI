import pytest
from unittest.mock import patch
from flask import Flask
from gig_routes import gig_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(gig_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("gig_routes.disconnect_platform")
def test_disconnect_platform_success(mock_disconnect, client):
    mock_disconnect.return_value = True
    response = client.delete("/gig/disconnect?user_id=1&platform=uber")
    assert response.status_code == 200
    assert b"Platform disconnected successfully" in response.data

def test_disconnect_platform_missing_params(client):
    response = client.delete("/gig/disconnect?user_id=1")
    assert response.status_code == 400
    assert b"Platform parameter is required" in response.data

@patch("gig_routes.disconnect_platform")
def test_disconnect_platform_failure(mock_disconnect, client):
    mock_disconnect.return_value = False
    response = client.delete("/gig/disconnect?user_id=1&platform=uber")
    assert response.status_code == 500
    assert b"Failed to disconnect platform" in response.data
