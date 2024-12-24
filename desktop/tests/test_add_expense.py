import pytest
from unittest.mock import Mock, patch, mock_open
from desktop.add_expense import process_receipt_ocr, add_expense, edit_expense

@pytest.fixture
def mock_database_connection():
    with patch('desktop.add_expense.get_database_connection') as mock_connection:
        mock_cursor = Mock()
        mock_connection.return_value.cursor.return_value = mock_cursor
        yield mock_connection

@pytest.fixture
def mock_requests():
    with patch('desktop.add_expense.requests') as mock_request:
        yield mock_request

def test_process_receipt_ocr_success(mock_requests):
    """Test successful Optical Character Recognition processing"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'text': 'Sample receipt text',
        'expense_id': 1,
        'document_id': 'doc123'
    }
    mock_requests.post.return_value = mock_response
    
    with patch('builtins.open', mock_open(read_data='test data')):
        result = process_receipt_ocr('test.jpg')
        
        assert result['text'] == 'Sample receipt text'
        assert result['expense_id'] == 1
        assert result['document_id'] == 'doc123'

def test_process_receipt_ocr_failure(mock_requests):
    """Test Optical Character Recognition processing failure"""
    mock_requests.post.return_value.status_code = 400
    
    with patch('builtins.open', mock_open(read_data='test data')):
        result = process_receipt_ocr('test.jpg')
        
        assert result is None

def test_add_expense_success(mock_database_connection, mock_requests):
    """Test successful expense addition"""
    mock_requests.post.return_value.status_code = 201
    
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = ['Test expense', '50.00', 'Food', '']
        
        add_expense()
        
        mock_requests.post.assert_called_once()
        assert 'Test expense' in str(mock_requests.post.call_args)

def test_add_expense_invalid_amount(mock_database_connection):
    """Test expense addition with invalid amount"""
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = ['Test expense', 'invalid', 'Food', '']
        with patch('builtins.print') as mock_print:
            add_expense()
            
            mock_print.assert_called_with("Error: Invalid amount format.")

def test_edit_expense_success(mock_database_connection):
    """Test successful expense editing"""
    mock_cursor = mock_database_connection.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = {
        'description': 'Old description',
        'amount': 50.0,
        'category': 'Food'
    }
    
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = ['1', 'New description', '75.0', 'Transport']
        
        edit_expense()
        
        mock_cursor.execute.assert_called()
        mock_database_connection.return_value.commit.assert_called_once()

def test_edit_expense_not_found(mock_database_connection):
    """Test editing non-existent expense"""
    mock_cursor = mock_database_connection.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None
    
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = ['999']
        with patch('builtins.print') as mock_print:
            edit_expense()
            
            mock_print.assert_called_with("Error: No expense found with ID 999.")
