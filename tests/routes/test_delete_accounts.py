import pytest
from api.routes.bank_routes import USER_TOKENS


def test_disconnect_bank_account_success(client):
    """Test disconnecting a bank account successfully."""
    # Mock the USER_TOKENS to simulate an existing token
    USER_TOKENS["1"] = "mock-token"

    response = client.post("/plaid/disconnect", json={"user_id": 1})

    assert response.status_code == 200
    assert b"Bank account disconnected successfully" in response.data
    assert "1" not in USER_TOKENS  # Ensure the token is removed


def test_disconnect_bank_account_missing_user_id(client):
    """Test failure to disconnect a bank account due to missing user_id."""
    response = client.post("/plaid/disconnect", json={})
    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data


def test_disconnect_bank_account_invalid_user_id(client):
    """Test failure to disconnect a bank account with invalid user_id."""
    response = client.post("/plaid/disconnect", json={"user_id": 999})
    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data
