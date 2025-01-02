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


@patch("gig_routes.fetch_expenses")
def test_fetch_expenses_success(mock_fetch_expenses, client):
    mock_fetch_expenses.return_value = [
        {"expense_id": "456", "platform": "lyft", "amount": "25.00"}
    ]
    response = client.get("/gig/expenses?user_id=1&platform=lyft")
    assert response.status_code == 200
    assert b"25.00" in response.data


def test_fetch_expenses_missing_user_id(client):
    response = client.get("/gig/expenses?platform=lyft")
    assert response.status_code == 400
    assert b"User ID is required" in response.data


@patch("gig_routes.fetch_expenses")
def test_fetch_expenses_no_data(mock_fetch_expenses, client):
    mock_fetch_expenses.return_value = []
    response = client.get("/gig/expenses?user_id=1&platform=lyft")
    assert response.status_code == 200
    assert b"No expenses found" in response.data
