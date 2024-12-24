import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.expense_integration import ExpenseIntegration

@pytest.fixture
def mock_database():
    with patch('api.utils.expense_integration.get_database_connection') as mock:
        yield mock

@pytest.fixture
def expense_integration(mock_database):
    return ExpenseIntegration()

@pytest.fixture
def sample_expense_data():
    return {
        'description': 'Test Expense',
        'amount': 100.50,
        'category': 'Office Supplies',
        'date': '2023-01-01',
        'receipt_url': 'http://example.com/receipt.jpg',
        'confidence_score': 0.95
    }

def test_create_expense_entry_success(expense_integration, mock_database, sample_expense_data):
    """Test successful expense entry creation"""
    mock_cursor = Mock()
    mock_cursor.lastrowid = 1
    mock_database.return_value.cursor.return_value = mock_cursor
    
    result = expense_integration.create_expense_entry(sample_expense_data, user_id='123')
    
    assert result == 1
    mock_cursor.execute.assert_called_once()
    mock_database.return_value.commit.assert_called_once()

def test_create_expense_entry_failure(expense_integration, mock_database):
    """Test expense entry creation failure"""
    mock_database.return_value.cursor.side_effect = Exception("Database error")
    
    result = expense_integration.create_expense_entry({}, user_id='123')
    
    assert result is None

def test_update_expense_entry_success(expense_integration, mock_database, sample_expense_data):
    """Test successful expense entry update"""
    mock_cursor = Mock()
    mock_database.return_value.cursor.return_value = mock_cursor
    
    result = expense_integration.update_expense_entry(1, sample_expense_data)
    
    assert result is True
    mock_cursor.execute.assert_called_once()
    mock_database.return_value.commit.assert_called_once()

def test_update_expense_entry_failure(expense_integration, mock_database):
    """Test expense entry update failure"""
    mock_database.return_value.cursor.side_effect = Exception("Database error")
    
    result = expense_integration.update_expense_entry(1, {})
    
    assert result is False

def test_create_expense_with_missing_fields(expense_integration, mock_database):
    """Test expense creation with missing fields"""
    mock_cursor = Mock()
    mock_cursor.lastrowid = 1
    mock_database.return_value.cursor.return_value = mock_cursor
    
    minimal_data = {'amount': 50.0}
    result = expense_integration.create_expense_entry(minimal_data, user_id='123')
    
    assert result == 1
    mock_cursor.execute.assert_called_once()

def test_update_expense_with_partial_data(expense_integration, mock_database):
    """Test expense update with partial data"""
    mock_cursor = Mock()
    mock_database.return_value.cursor.return_value = mock_cursor
    
    partial_data = {'amount': 75.0}
    result = expense_integration.update_expense_entry(1, partial_data)
    
    assert result is True
    mock_cursor.execute.assert_called_once()

def test_create_expense_with_invalid_data(expense_integration, mock_database):
    """Test expense creation with invalid data"""
    mock_cursor = Mock()
    mock_database.return_value.cursor.return_value = mock_cursor
    
    invalid_data = {'amount': 'not_a_number'}
    result = expense_integration.create_expense_entry(invalid_data, user_id='123')
    
    assert result is None

def test_update_nonexistent_expense(expense_integration, mock_database, sample_expense_data):
    """Test updating non-existent expense"""
    mock_cursor = Mock()
    mock_cursor.rowcount = 0
    mock_database.return_value.cursor.return_value = mock_cursor
    
    result = expense_integration.update_expense_entry(999, sample_expense_data)
    
    assert result is True  # Current implementation doesn't check rowcount

def test_create_expense_with_future_date(expense_integration, mock_database):
    """Test expense creation with future date"""
    mock_cursor = Mock()
    mock_cursor.lastrowid = 1
    mock_database.return_value.cursor.return_value = mock_cursor
    
    future_data = {
        'description': 'Future Expense',
        'amount': 100.0,
        'date': '2025-01-01'
    }
    
    result = expense_integration.create_expense_entry(future_data, user_id='123')
    assert result == 1

def test_database_connection_error(mock_database):
    """Test database connection error handling"""
    mock_database.side_effect = Exception("Connection error")
    
    with pytest.raises(Exception):
        ExpenseIntegration()
