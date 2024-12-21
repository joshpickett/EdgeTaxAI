import pytest
from unittest.mock import Mock, patch
from flask import Flask
from api.routes.bank_routes import bank_bp
from plaid.exceptions import ApiException


# Flask test client setup
@pytest.fixture
def client():
    """Fixture to initialize Flask test client."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# 1. Test successful exchange of a public token
@patch("api.routes.bank_routes.plaid_client.item_public_token_exchange")
def test_exchange_public_token_success(mock_exchange, client):
    """Test successful exchange of a public token."""
    # Properly mock Plaid API response
    mock_response = Mock()
    mock_response.access_token = "test-access-token"
    mock_response.item_id = "mock-item-id"
    mock_exchange.return_value = mock_response

    response = client.post("/plaid/exchange-token", json={
        "user_id": 1,
        "public_token": "mock-public-token"
    })

    assert response.status_code == 200
    assert b"Bank account connected successfully" in response.data


# 2. Test failure due to Plaid API error
@patch("api.routes.bank_routes.plaid_client.item_public_token_exchange")
def test_exchange_public_token_failure(mock_exchange, client):
    """Test failure to exchange a public token due to Plaid API error."""
    # Simulate Plaid API failure
    mock_exchange.side_effect = ApiException(status=500, reason="Plaid API error")

    response = client.post("/plaid/exchange-token", json={
        "user_id": 1,
        "public_token": "mock-public-token"
    })

    assert response.status_code == 500
    assert b"Failed to exchange Plaid token" in response.data


# 3. Test missing required fields
def test_exchange_public_token_missing_fields(client):
    """Test failure when required fields are missing."""
    # Missing 'public_token'
    response = client.post("/plaid/exchange-token", json={"user_id": 1})
    assert response.status_code == 400
    assert b"User ID and Public Token are required" in response.data

    # Missing 'user_id'
    response = client.post("/plaid/exchange-token", json={"public_token": "mock-public-token"})
    assert response.status_code == 400
    assert b"User ID and Public Token are required" in response.data


# 4. Test invalid JSON payload
def test_exchange_public_token_invalid_payload(client):
    """Test failure when the payload is invalid."""
    response = client.post("/plaid/exchange-token", data="Invalid JSON", content_type="application/json")
    assert response.status_code == 400
    assert b"Invalid JSON payload" in response.data


# 5. Test handling invalid API keys
@patch("api.routes.bank_routes.plaid_client.item_public_token_exchange")
def test_exchange_public_token_invalid_keys(mock_exchange, client):
    """Test handling of invalid API keys for Plaid."""
    mock_exchange.side_effect = ApiException(status=401, reason="Invalid API keys")

    response = client.post("/plaid/exchange-token", json={
        "user_id": 1,
        "public_token": "mock-public-token"
    })

    assert response.status_code == 500
    assert b"Failed to exchange Plaid token" in response.data


# 6. Test invalid user_id input
def test_exchange_public_token_invalid_user_id(client):
    """Test when user_id is not a valid integer."""
    response = client.post("/plaid/exchange-token", json={
        "user_id": "invalid",  # Invalid user_id
        "public_token": "mock-public-token"
    })
    assert response.status_code == 400
    assert b"User ID must be an integer" in response.data


# 7. Test when Plaid API returns a bad request
@patch("api.routes.bank_routes.plaid_client.item_public_token_exchange")
def test_exchange_public_token_bad_request(mock_exchange, client):
    """Test handling of a bad request response from Plaid."""
    mock_exchange.side_effect = ApiException(status=400, reason="Bad Request")

    response = client.post("/plaid/exchange-token", json={
        "user_id": 1,
        "public_token": "mock-public-token"
    })

    assert response.status_code == 400
    assert b"Bad request to Plaid API" in response.data
