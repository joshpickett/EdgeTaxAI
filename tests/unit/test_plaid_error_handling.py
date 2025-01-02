import pytest
from flask import Flask
from api.routes.bank_routes import bank_bp
from unittest.mock import patch


@pytest.fixture
def client():
    """Flask test client for bank routes."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_plaid_api_error_handling(client, mocker):
    """Test error handling when Plaid API fails."""
    # Simulate Plaid API error
    mocker.patch(
        "api.routes.bank_routes.plaid_client.transactions_get",
        side_effect=Exception("Plaid API error"),
    )

    response = client.get(
        "/plaid/transactions",
        query_string={
            "user_id": "1",
            "start_date": "2024-12-01",
            "end_date": "2024-12-19",
        },
    )

    assert response.status_code == 500
    assert b"Failed to fetch transactions" in response.data
