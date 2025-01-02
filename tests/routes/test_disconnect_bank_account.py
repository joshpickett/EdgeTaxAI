import pytest
from flask import Flask
from api.routes.bank_routes import bank_bp, USER_TOKENS
from unittest.mock import patch


@pytest.fixture
def client():
    """Fixture to create a Flask test client for the bank routes."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_disconnect_bank_account_success(client):
    """Test successfully disconnecting a bank account."""
    # Prepopulate USER_TOKENS for testing
    USER_TOKENS[1] = "mock-encrypted-access-token"

    response = client.post("/plaid/disconnect", json={"user_id": 1})

    assert response.status_code == 200
    assert b"Bank account disconnected successfully" in response.data
    assert 1 not in USER_TOKENS  # Ensure token was removed


def test_disconnect_bank_account_missing_user_id(client):
    """Test failure when user_id is missing."""
    response = client.post("/plaid/disconnect", json={})

    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data


def test_disconnect_bank_account_invalid_user_id(client):
    """Test failure when user_id is not valid."""
    response = client.post("/plaid/disconnect", json={"user_id": "invalid_id"})

    assert response.status_code == 400
    assert b"Invalid or missing User ID" in response.data


def test_disconnect_bank_account_user_not_found(client):
    """Test failure when user_id is not found in USER_TOKENS."""
    response = client.post("/plaid/disconnect", json={"user_id": 2})

    assert response.status_code == 404
    assert b"User ID not found" in response.data


def test_disconnect_bank_account_server_error(client):
    """Test internal server error during disconnect."""
    # Use a custom mutable dictionary to replace USER_TOKENS to allow `pop` patching
    with patch(
        "api.routes.bank_routes.USER_TOKENS",
        new_callable=lambda: {1: "mock-encrypted-access-token"},
    ):
        with patch.object(
            USER_TOKENS, "pop", side_effect=Exception("Unexpected error")
        ):
            response = client.post("/plaid/disconnect", json={"user_id": 1})

            assert response.status_code == 500
            assert b"Failed to disconnect bank account" in response.data
