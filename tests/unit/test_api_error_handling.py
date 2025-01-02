import pytest
from unittest.mock import patch
from flask import Flask
from api.routes.bank_routes import bank_bp


@pytest.fixture
def client():
    """Fixture to set up a Flask test client for the bank routes."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Test Case: Plaid API Failure during link token creation
@patch("api.routes.bank_routes.plaid_client.link_token_create")
def test_plaid_link_token_api_failure(mock_link_token_create, client):
    """Test handling of Plaid API failures for link token creation."""
    mock_link_token_create.side_effect = Exception("Plaid API error")

    response = client.post("/plaid/link-token", json={"user_id": 1})

    assert response.status_code == 500
    assert b"Failed to generate Plaid link token" in response.data


# Test Case: Plaid API Failure during public token exchange
@patch("api.routes.bank_routes.plaid_client.item_public_token_exchange")
def test_plaid_public_token_exchange_api_failure(mock_exchange, client):
    """Test handling of Plaid API failures during public token exchange."""
    mock_exchange.side_effect = Exception("Plaid API error")

    response = client.post(
        "/plaid/exchange-token", json={"user_id": 1, "public_token": "mock-token"}
    )

    assert response.status_code == 500
    assert b"Failed to exchange Plaid token" in response.data


# Test Case: Plaid API Failure during account fetching
@patch("api.routes.bank_routes.plaid_client.accounts_get")
def test_plaid_accounts_api_failure(mock_accounts_get, client):
    """Test handling of Plaid API failures when fetching bank accounts."""
    mock_accounts_get.side_effect = Exception("Plaid API error")

    response = client.get("/plaid/accounts?user_id=1")

    assert response.status_code == 500
    assert b"Failed to fetch accounts" in response.data


# Test Case: Plaid API Failure during transaction fetching
@patch("api.routes.bank_routes.plaid_client.transactions_get")
def test_plaid_transactions_api_failure(mock_transactions_get, client):
    """Test handling of Plaid API failures when fetching transactions."""
    mock_transactions_get.side_effect = Exception("Plaid API error")

    response = client.get(
        "/plaid/transactions?user_id=1&start_date=2024-12-01&end_date=2024-12-20"
    )

    assert response.status_code == 500
    assert b"Failed to fetch transactions" in response.data
