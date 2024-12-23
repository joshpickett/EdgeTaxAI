import pytest
from flask import Flask, json
from unittest.mock import patch, Mock
from ...routes.bank_routes import bank_bp
from plaid.exceptions import PlaidError

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_plaid():
    """Mock Plaid client"""
    with patch('api.routes.bank_routes.get_plaid_client') as mock:
        yield mock

def test_create_link_token_success(client, mock_plaid, mock_redis):
    """Test successful link token creation"""
    mock_plaid.return_value.link_token_create.return_value = Mock(
        link_token="test_link_token"
    )
    
    response = client.post(
        '/plaid/link-token',
        data=json.dumps({"user_id": 1}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert "test_link_token" in response.get_json()["link_token"]

def test_create_link_token_invalid_user(client):
    """Test link token creation with invalid user"""
    response = client.post(
        '/plaid/link-token',
        data=json.dumps({"user_id": "invalid"}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert b"User ID must be an integer" in response.data

def test_exchange_token_success(client, mock_plaid):
    """Test successful token exchange"""
    mock_plaid.return_value.item_public_token_exchange.return_value = Mock(
        access_token="test_access_token"
    )
    
    data = {
        "user_id": 1,
        "public_token": "test_public_token"
    }
    
    response = client.post(
        '/plaid/exchange-token',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert b"Bank account connected successfully" in response.data

def test_get_accounts_success(client, mock_plaid, mock_redis):
    """Test successful account retrieval"""
    mock_plaid.return_value.accounts_get.return_value = Mock(
        accounts=[{"id": "1", "name": "Test Account"}]
    )
    
    response = client.get('/plaid/accounts?user_id=1')
    
    assert response.status_code == 200
    assert "Test Account" in str(response.data)

def test_get_accounts_cached(client, mock_redis):
    """Test cached account retrieval"""
    cached_data = {"accounts": [{"id": "1", "name": "Cached Account"}]}
    mock_redis.get.return_value = json.dumps(cached_data)
    
    response = client.get('/plaid/accounts?user_id=1')
    
    assert response.status_code == 200
    assert "Cached Account" in str(response.data)

def test_get_transactions_success(client, mock_plaid, mock_redis):
    """Test successful transaction retrieval"""
    mock_plaid.return_value.transactions_get.return_value = Mock(
        transactions=[{
            "id": "1",
            "amount": 100.00,
            "date": "2023-01-01"
        }]
    )
    
    response = client.get(
        '/plaid/transactions?user_id=1&start_date=2023-01-01&end_date=2023-01-31'
    )
    
    assert response.status_code == 200
    assert "100.00" in str(response.data)

def test_refresh_token_success(client, mock_plaid):
    """Test successful token refresh"""
    mock_plaid.return_value.item_public_token_exchange.return_value = Mock(
        access_token="new_access_token"
    )
    
    data = {
        "user_id": 1,
        "platform": "plaid"
    }
    
    response = client.post(
        '/refresh-token',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert b"Token refreshed successfully" in response.data

def test_handle_plaid_error(client, mock_plaid):
    """Test Plaid error handling"""
    mock_plaid.return_value.link_token_create.side_effect = PlaidError(
        type="INVALID_REQUEST",
        code="INVALID_FIELD",
        message="Test error"
    )
    
    response = client.post(
        '/plaid/link-token',
        data=json.dumps({"user_id": 1}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert b"Test error" in response.data
