import pytest
from unittest.mock import Mock, patch
from api.add_expense import add_expense, edit_expense, process_receipt_ocr

@pytest.fixture
def mock_expense_service():
    with patch('api.services.expense_service_adapter.ExpenseServiceAdapter') as mock:
        yield mock

@pytest.fixture
def mock_sync_manager():
    with patch('api.utils.sync_manager.SyncManager') as mock:
        yield mock

def test_add_expense_success(mock_expense_service, mock_sync_manager):
    # Arrange
    expense_data = {
        "description": "Test expense",
        "amount": 100.00,
        "category": "test"
    }
    mock_expense_service.create_expense.return_value = True
    
    # Act
    result = add_expense(expense_data)
    
    # Assert
    assert result is True
    mock_expense_service.create_expense.assert_called_once_with(expense_data)
    mock_sync_manager.sync_expenses.assert_called_once()

def test_add_expense_invalid_amount():
    # Arrange
    expense_data = {
        "description": "Test expense",
        "amount": -100.00,
        "category": "test"
    }
    
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        add_expense(expense_data)
    assert "Amount must be positive" in str(exc.value)

def test_process_receipt_ocr_success(mock_expense_service):
    # Arrange
    mock_expense_service.process_receipt.return_value = {
        "text": "Test receipt",
        "amount": 100.00
    }
    
    # Act
    result = process_receipt_ocr("test_receipt.jpg")
    
    # Assert
    assert result["text"] == "Test receipt"
    assert result["amount"] == 100.00

def test_edit_expense_success(mock_expense_service):
    # Arrange
    expense_id = 1
    updated_data = {
        "description": "Updated expense",
        "amount": 150.00
    }
    mock_expense_service.update_expense.return_value = True
    
    # Act
    result = edit_expense(expense_id, updated_data)
    
    # Assert
    assert result is True
    mock_expense_service.update_expense.assert_called_once_with(expense_id, updated_data)
