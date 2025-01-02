import pytest
from flask import Flask
from api.routes.mileage_routes import mileage_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(mileage_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add_mileage_invalid_date(client):
    response = client.post(
        "/mileage/add",
        json={
            "user_id": 1,
            "start_location": "Start",
            "end_location": "End",
            "date": "invalid-date",
        },
    )
    assert response.status_code == 400
    assert "Invalid date format" in response.json["error"]
