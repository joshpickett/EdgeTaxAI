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

def test_categorization_fallback(client, mocker):
    """Test fallback to 'General' category when categorization fails."""
    mocker.patch("api.routes.bank_routes.categorize_transaction", return_value=None)

    response = client.post("/fetch-transactions", json={
        "access_token": "valid_token",
        "account_id": "account_123",
        "start_date": "2024-12-01",
        "end_date": "2024-12-19"
    })

    assert response.status_code == 200
    assert b'"category":"General"' in response.data
