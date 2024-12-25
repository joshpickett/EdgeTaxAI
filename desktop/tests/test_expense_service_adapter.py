import pytest
from unittest.mock import Mock, patch
from desktop.services.expense_service_adapter import ExpenseServiceAdapter

@pytest.fixture
def expense_service():
    return ExpenseServiceAdapter(base_url="http://test-api")

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post:
        yield mock_post

def test_create_expense_success(expense_service, mock_requests):
    # Arrange
    expense_data = {
        "description": "Test expense",
        "amount": 100.00,
        "category": "test"
    }
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, **expense_data}
    mock_requests.return_value = mock_response

    # Act
    result = expense_service.create_expense(expense_data)

    # Assert
    assert result == {"id": 1, **expense_data}
    mock_requests.assert_called_once_with(
        "http://test-api/expenses",
        json=expense_data
    )

def test_create_expense_failure(expense_service, mock_requests):
    # Arrange
    mock_requests.side_effect = Exception("API Error")

    # Act
    result = expense_service.create_expense({})

    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_sync_platform_data_success(expense_service, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Act
    result = await expense_service.sync_platform_data("uber")

    # Assert
    assert result is True
    mock_requests.assert_called_once()

@pytest.mark.asyncio
async def test_sync_platform_data_invalid_platform(expense_service):
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        await expense_service.sync_platform_data("invalid_platform")
    assert "Invalid platform" in str(exc.value)

@pytest.mark.asyncio
async def test_sync_platform_data_failure(expense_service, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 500
    mock_requests.return_value = mock_response

    # Act
    result = await expense_service.sync_platform_data("uber")

    # Assert
    assert result is False
