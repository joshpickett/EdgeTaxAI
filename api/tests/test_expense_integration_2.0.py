import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from ..utils.expense_integration import ExpenseIntegration


class TestExpenseIntegration:
    @pytest.fixture
    def expense_integration(self):
        return ExpenseIntegration()

    @pytest.fixture
    def mock_database(self):
        with patch("sqlite3.connect") as mock:
            yield mock

    def test_create_expense_entry_success(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        expense_data = {
            "description": "Test Expense",
            "amount": 100.00,
            "category": "Office Supplies",
            "date": "2023-12-01",
            "receipt_url": "http://example.com/receipt.jpg",
            "confidence_score": 0.95,
        }

        result = expense_integration.create_expense_entry(expense_data, "user123")

        assert result == 1
        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()

    def test_update_expense_entry_success(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor

        expense_data = {
            "description": "Updated Expense",
            "amount": 150.00,
            "category": "Travel",
            "date": "2023-12-02",
            "receipt_url": "http://example.com/receipt2.jpg",
            "confidence_score": 0.98,
        }

        result = expense_integration.update_expense_entry(1, expense_data)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()

    def test_create_expense_entry_missing_fields(self, expense_integration):
        expense_data = {
            "description": "Test Expense"
            # Missing required fields
        }

        result = expense_integration.create_expense_entry(expense_data, "user123")
        assert result is None

    def test_update_expense_entry_invalid_id(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        expense_data = {"description": "Updated Expense", "amount": 150.00}

        result = expense_integration.update_expense_entry(999, expense_data)
        assert result is False

    def test_create_expense_with_ocr_data(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        ocr_data = {
            "description": "Office Supplies from OCR",
            "amount": 75.50,
            "category": "Office Supplies",
            "date": "2023-12-01",
            "receipt_url": "http://example.com/receipt.jpg",
            "confidence_score": 0.85,
        }

        result = expense_integration.create_expense_entry(ocr_data, "user123")

        assert result == 1
        assert mock_cursor.execute.call_count == 1

    def test_expense_validation(self, expense_integration):
        invalid_test_cases = [
            {"amount": -100.00},  # Negative amount
            {"amount": "invalid"},  # Invalid amount type
            {"date": "invalid-date"},  # Invalid date format
            {"confidence_score": 1.5},  # Invalid confidence score
        ]

        for invalid_data in invalid_test_cases:
            result = expense_integration.create_expense_entry(invalid_data, "user123")
            assert result is None

    def test_expense_categorization(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        expense_data = {
            "description": "Uber ride to airport",
            "amount": 50.00,
            "category": None,  # Category should be auto-assigned
        }

        result = expense_integration.create_expense_entry(expense_data, "user123")

        assert result == 1
        # Verify category was assigned
        execute_call = mock_cursor.execute.call_args[0]
        assert "Travel" in str(execute_call) or "Transportation" in str(execute_call)

    def test_batch_expense_creation(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        expenses = [
            {"description": "Expense 1", "amount": 100.00},
            {"description": "Expense 2", "amount": 200.00},
        ]

        results = []
        for expense in expenses:
            result = expense_integration.create_expense_entry(expense, "user123")
            results.append(result)

        assert all(result is not None for result in results)
        assert mock_cursor.execute.call_count == len(expenses)

    def test_expense_sync_status(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        expense_data = {
            "description": "Test Expense",
            "amount": 100.00,
            "sync_status": "pending",
        }

        result = expense_integration.create_expense_entry(expense_data, "user123")

        assert result == 1
        # Verify sync status was saved
        execute_call = mock_cursor.execute.call_args[0]
        assert "pending" in str(execute_call)

    def test_expense_metadata_handling(self, expense_integration, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        expense_data = {
            "description": "Test Expense",
            "amount": 100.00,
            "metadata": {
                "tax_category": "business",
                "project_id": "PROJ123",
                "custom_field": "value",
            },
        }

        result = expense_integration.create_expense_entry(expense_data, "user123")

        assert result == 1
        # Verify metadata was properly handled
        execute_call = mock_cursor.execute.call_args[0]
        assert "metadata" in str(execute_call)
