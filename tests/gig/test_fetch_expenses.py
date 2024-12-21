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

@patch("gig_routes.fetch_trips")
def test_fetch_trips_success(mock_fetch_trips, client):
    mock_fetch_trips.return_value = [{"trip_id": "123", "platform": "uber", "distance": "10 miles"}]
    response = client.get("/gig/trips?user_id=1&platform=uber")
    assert response.status_code == 200
    assert b"uber" in response.data

def test_fetch_trips_missing_user_id(client):
    response = client.get("/gig/trips?platform=uber")
    assert response.status_code == 400
    assert b"User ID is required" in response.data

@patch("gig_routes.fetch_trips")
def test_fetch_trips_no_data(mock_fetch_trips, client):
    mock_fetch_trips.return_value = []
    response = client.get("/gig/trips?user_id=1&platform=uber")
    assert response.status_code == 200
    assert b"No trips found" in response.data
