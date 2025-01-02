import pytest
from unittest.mock import patch
from flask import Flask
from api.routes.mileage_routes import mileage_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(mileage_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("api.routes.mileage_routes.fetch_google_directions")
def test_add_mileage_success(mock_google_api, client):
    mock_google_api.return_value = ("10 miles", None)

    response = client.post(
        "/mileage/add",
        json={
            "user_id": 1,
            "start_location": "123 Start St",
            "end_location": "456 End Ave",
            "date": "2024-01-01",
        },
    )

    assert response.status_code == 201
    assert "distance" in response.json
    assert response.json["distance"] == "10 miles"
