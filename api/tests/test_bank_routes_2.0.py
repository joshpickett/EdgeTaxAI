import pytest
import jwt
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from ..routes.bank_routes import bank_bp
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

@pytest.fixture
def app():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_plaid_client():
    with patch('plaid.api.plaid_api.PlaidApi') as mock:
        yield mock

class TestBankRoutes:
    def test_create_link_token_success(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.link_token = "test_link_token"
        mock_plaid_client.return_value.link_token_create.return_value = mock_response

        response = client.post('/plaid/link-token', 
                             json={"user_id": 123})
        
        assert response.status_code == 200
        assert "link_token" in response.json

    def test_create_link_token_missing_user_id(self, client):
        response = client.post('/plaid/link-token', json={})
        assert response.status_code == 400
        assert "error" in response.json

    def test_exchange_token_success(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.access_token = "test_access_token"
        mock_plaid_client.return_value.item_public_token_exchange.return_value = mock_response

        response = client.post('/plaid/exchange-token',
                             json={
                                 "public_token": "test_public_token",
                                 "user_id": 123
                             })
        
        assert response.status_code == 200
        assert "message" in response.json

    def test_get_accounts_success(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.accounts = [{"id": "test_account"}]
        mock_plaid_client.return_value.accounts_get.return_value = mock_response

        response = client.get('/plaid/accounts?user_id=123')
        assert response.status_code == 200
        assert "accounts" in response.json

    def test_get_transactions_success(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.transactions = [{"id": "test_transaction"}]
        mock_plaid_client.return_value.transactions_get.return_value = mock_response

        response = client.get('/plaid/transactions?user_id=123')
        assert response.status_code == 200
        assert "transactions" in response.json

    def test_get_balance_success(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.accounts = [
            {"account_id": "123", "balances": {"current": 1000}}
        ]
        mock_plaid_client.return_value.accounts_balance_get.return_value = mock_response

        response = client.get('/plaid/balance?user_id=123')
        assert response.status_code == 200
        assert "balances" in response.json

    def test_disconnect_bank_success(self, client):
        response = client.post('/plaid/disconnect',
                             json={"user_id": 123})
        assert response.status_code == 200
        assert "message" in response.json

    def test_rate_limit_exceeded(self, client):
        # Simulate rate limit exceeded
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.get.return_value = b'101'  # Over limit
            response = client.post('/plaid/link-token',
                                 json={"user_id": 123})
            assert response.status_code == 429

    @patch('plaid.api.plaid_api.PlaidApi.transactions_get')
    def test_transaction_search(self, mock_transactions_get, client):
        mock_transactions_get.return_value.transactions = [
            {"id": "tx1", "amount": 100}
        ]
        
        response = client.post('/plaid/transactions/search',
                             json={
                                 "user_id": 123,
                                 "filters": {
                                     "start_date": "2023-01-01",
                                     "end_date": "2023-12-31"
                                 }
                             })
        assert response.status_code == 200
        assert "transactions" in response.json

    def test_verify_account_status(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.accounts = [
            {
                "account_id": "123",
                "verification_status": "verified"
            }
        ]
        mock_plaid_client.return_value.accounts_get.return_value = mock_response

        response = client.get('/plaid/verify?user_id=123')
        assert response.status_code == 200
        assert "verification_status" in response.json

    def test_analyze_transactions(self, client, mock_plaid_client):
        mock_response = Mock()
        mock_response.transactions = [
            {"amount": 100, "merchant_name": "Test Store"}
        ]
        mock_plaid_client.return_value.transactions_get.return_value = mock_response

        response = client.get('/plaid/transactions/analysis?user_id=123')
        assert response.status_code == 200
        assert "analysis" in response.json
