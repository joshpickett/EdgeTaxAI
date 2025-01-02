import pytest
from flask import Flask
from gig_routes import gig_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(gig_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_connect_valid_platform(client):
    response = client.get("/gig/connect?platform=uber")
    assert response.status_code == 302
    assert response.location == "https://uber.com/oauth/authorize"


def test_connect_invalid_platform(client):
    response = client.get("/gig/connect?platform=invalid_platform")
    assert response.status_code == 400
    assert b"Invalid platform specified" in response.data


def test_connect_missing_platform(client):
    response = client.get("/gig/connect")
    assert response.status_code == 400
    assert b"Platform parameter is required" in response.data
