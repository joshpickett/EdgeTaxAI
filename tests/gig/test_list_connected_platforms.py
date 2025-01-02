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


@patch("gig_routes.fetch_user_connections")
def test_list_connected_platforms_success(mock_fetch, client):
    mock_fetch.return_value = [{"platform": "uber", "status": "connected"}]
    response = client.get("/gig/connections?user_id=1")
    assert response.status_code == 200
    assert b"uber" in response.data


def test_list_connected_platforms_missing_user_id(client):
    response = client.get("/gig/connections")
    assert response.status_code == 400
    assert b"User ID is required" in response.data


@patch("gig_routes.fetch_user_connections")
def test_list_connected_platforms_empty(mock_fetch, client):
    mock_fetch.return_value = []
    response = client.get("/gig/connections?user_id=1")
    assert response.status_code == 200
    assert b"No connected platforms" in response.data
