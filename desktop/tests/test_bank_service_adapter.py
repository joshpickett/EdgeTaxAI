import pytest
from unittest.mock import Mock, patch
from desktop.services.bank_service_adapter import BankServiceAdapter

@pytest.fixture
def bank_service():
    return BankServiceAdapter(base_url="http://test-api")

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post:
        yield mock_post

async def test_get_link_token_success(bank_service, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"link_token": "test-token"}
    mock_requests.return_value = mock_response

    # Act
    result = await bank_service.get_link_token("test-user")

    # Assert
    assert result == "test-token"
    mock_requests.assert_called_once_with(
        "http://test-api/banks/plaid/link-token",
        json={"user_id": "test-user"},
        headers={"Content-Type": "application/json"}
    )

async def test_get_link_token_failure(bank_service, mock_requests):
    # Arrange
    mock_requests.side_effect = Exception("API Error")

    # Act
    result = await bank_service.get_link_token("test-user")

    # Assert
    assert result is None

async def test_exchange_token_success(bank_service, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "test-access-token"}
    mock_requests.return_value = mock_response

    # Act
    result = await bank_service.exchange_token("public-token", "test-user")

    # Assert
    assert result == {"access_token": "test-access-token"}
    mock_requests.assert_called_once_with(
        "http://test-api/banks/plaid/exchange-token",
        json={"public_token": "public-token", "user_id": "test-user"},
        headers={"Content-Type": "application/json"}
    )

async def test_exchange_token_failure(bank_service, mock_requests):
    # Arrange
    mock_requests.side_effect = Exception("API Error")

    # Act
    result = await bank_service.exchange_token("public-token", "test-user")

    # Assert
    assert result is None
