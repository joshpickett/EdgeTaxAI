import pytest
from unittest.mock import Mock, patch
from flask import Flask
from api.routes.bank_routes import bank_bp, USER_TOKENS
from plaid.exceptions import ApiException


@pytest.fixture
def client():
    """Fixture to initialize Flask test client."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# 1. Test successful fetching of bank accounts
@patch("api.routes.bank_routes.plaid_client.accounts_get")
def test_fetch_bank_accounts_success(mock_accounts_get, client):
    """Test successful fetching of bank accounts."""
    USER_TOKENS[1] = "mock-access-token"

    # Mock Plaid API response with valid accounts
    mock_response = Mock()
    mock_response.to_dict.return_value = {
        "accounts": [
            {"name": "Checking Account", "balance": {"current": 500}},
            {"name": "Savings Account", "balance": {"current": 1500}}
        ]
    }
    mock_accounts_get.return_value = mock_response

    response = client.get("/plaid/accounts?user_id=1")

    assert response.status_code == 200
    assert b"Checking Account" in response.data
    assert b"Savings Account" in response.data
    assert b"accounts" in response.data


# 2. Test failure due to invalid user ID
def test_fetch_bank_accounts_invalid_user(client):
    """Test fetching accounts with an invalid or missing user ID."""
    response = client.get("/plaid/accounts?user_id=999")

    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data


# 3. Test failure due to Plaid API error
@patch("api.routes.bank_routes.plaid_client.accounts_get")
def test_fetch_bank_accounts_failure(mock_accounts_get, client):
    """Test failure when Plaid API throws an exception."""
    USER_TOKENS[1] = "mock-access-token"

    # Simulate Plaid API failure
    mock_accounts_get.side_effect = ApiException("Plaid API error")

    response = client.get("/plaid/accounts?user_id=1")

    assert response.status_code == 500
    assert b"Failed to fetch accounts" in response.data


# 4. Test failure due to invalid access token
@patch("api.routes.bank_routes.plaid_client.accounts_get")
def test_fetch_bank_accounts_invalid_token(mock_accounts_get, client):
    """Test failure when the access token is invalid."""
    USER_TOKENS[1] = "invalid-access-token"

    # Simulate Plaid API response with invalid token
    mock_accounts_get.side_effect = ApiException("Invalid token")

    response = client.get("/plaid/accounts?user_id=1")

    assert response.status_code == 500
    assert b"Failed to fetch accounts" in response.data


# 5. Test failure when no access token exists for the user
def test_fetch_bank_accounts_no_token(client):
    """Test failure when no token exists for the user."""
    response = client.get("/plaid/accounts?user_id=1")

    assert response.status_code == 400
    assert b"No access token exists for the provided User ID" in response.data
