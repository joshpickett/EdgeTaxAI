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


# Test Case: Successful creation of Plaid Link Token
@patch("api.routes.bank_routes.plaid_client.link_token_create")
def test_create_link_token_success(mock_link_token_create, client):
    """Test successful creation of a Plaid link token."""
    # Mock Plaid API response as an object with attributes
    mock_link_token_create.return_value = type(
        "MockResponse", (object,), {"link_token": "test-link-token"}
    )

    # Perform API request
    response = client.post("/plaid/link-token", json={"user_id": 1})

    # Assertions
    assert response.status_code == 200
    assert b"test-link-token" in response.data
    mock_link_token_create.assert_called_once()


# Test Case: Missing User ID
def test_create_link_token_missing_user_id(client):
    """Test failure when user_id is missing."""
    response = client.post("/plaid/link-token", json={})
    assert response.status_code == 400
    assert b"User ID is required" in response.data


# Test Case: Failure due to Plaid API Error
@patch("api.routes.bank_routes.plaid_client.link_token_create")
def test_create_link_token_failure(mock_link_token_create, client):
    """Test failure to create Plaid link token due to API error."""
    # Mock API error
    mock_link_token_create.side_effect = Exception("Plaid API error")

    # Perform API request
    response = client.post("/plaid/link-token", json={"user_id": 1})

    # Assertions
    assert response.status_code == 500
    assert b"Failed to generate Plaid link token" in response.data
    mock_link_token_create.assert_called_once()


# Test Case: Invalid User ID
def test_create_link_token_invalid_user_id(client):
    """Test failure when user_id is invalid."""
    response = client.post("/plaid/link-token", json={"user_id": "invalid"})
    assert response.status_code == 400
    assert b"User ID must be an integer" in response.data


# Test Case: Empty JSON Request
def test_create_link_token_empty_request(client):
    """Test failure when JSON payload is empty."""
    response = client.post("/plaid/link-token", json=None)
    assert response.status_code == 400
    assert b"User ID is required" in response.data


# Test Case: Missing Plaid Client Configuration
@patch(
    "api.routes.bank_routes.plaid_client.link_token_create",
    side_effect=AttributeError("Plaid client not configured"),
)
def test_create_link_token_missing_plaid_client(mock_link_token_create, client):
    """Test failure when Plaid client is not properly configured."""
    response = client.post("/plaid/link-token", json={"user_id": 1})
    assert response.status_code == 500
    assert b"Plaid client not configured properly" in response.data
