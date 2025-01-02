import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
from flask import Flask
from api.routes.bank_routes import bank_bp


@pytest.fixture
def client():
    """Fixture for creating a test client."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("api.routes.bank_routes.plaid_client.transactions_get")
def test_fetch_transactions_success(mock_transactions_get, client):
    """Test successful fetching of transactions."""
    # Mock Plaid API response with transactions attribute
    mock_response = Mock()
    mock_response.transactions = [
        {"name": "Test Transaction", "amount": 10.0, "date": "2024-12-01"},
        {"name": "Test Transaction 2", "amount": 20.0, "date": "2024-12-02"},
    ]
    mock_transactions_get.return_value = mock_response

    # Correct date input as required by Plaid's API
    response = client.get(
        "/plaid/transactions?user_id=1&start_date=2024-12-01&end_date=2024-12-20"
    )

    assert response.status_code == 200
    assert b"Test Transaction" in response.data
    assert b"Test Transaction 2" in response.data


@patch("api.routes.bank_routes.plaid_client.transactions_get")
def test_fetch_transactions_missing_fields(mock_transactions_get, client):
    """Test fetching transactions with missing user_id."""
    response = client.get(
        "/plaid/transactions?start_date=2024-12-01&end_date=2024-12-20"
    )

    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data


@patch("api.routes.bank_routes.plaid_client.transactions_get")
def test_fetch_transactions_invalid_date(mock_transactions_get, client):
    """Test fetching transactions with invalid date format."""
    response = client.get(
        "/plaid/transactions?user_id=1&start_date=invalid-date&end_date=2024-12-20"
    )

    assert response.status_code == 400
    assert b"Invalid date format" in response.data


@patch("api.routes.bank_routes.plaid_client.transactions_get")
def test_fetch_transactions_failure(mock_transactions_get, client):
    """Test handling of API failure during transaction fetch."""
    # Mock API failure
    mock_transactions_get.side_effect = Exception("Plaid API error")

    response = client.get(
        "/plaid/transactions?user_id=1&start_date=2024-12-01&end_date=2024-12-20"
    )

    assert response.status_code == 500
    assert b"Failed to fetch transactions" in response.data


def test_fetch_transactions_invalid_request_params(client):
    """Test handling of invalid or missing parameters."""
    response = client.get("/plaid/transactions", json={"bad_field": "invalid"})

    assert response.status_code == 400
    assert b"Invalid request parameters" in response.data


@patch("api.routes.bank_routes.plaid_client.transactions_get")
def test_fetch_transactions_no_user_id(mock_transactions_get, client):
    """Test when no user_id is provided."""
    response = client.get(
        "/plaid/transactions?start_date=2024-12-01&end_date=2024-12-20"
    )

    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data
