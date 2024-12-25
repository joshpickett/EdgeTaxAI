import pytest
from unittest.mock import Mock, patch
from tkinter import Tk
from desktop.dashboard import ExpenseDashboard

@pytest.fixture
def mock_api():
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:
        yield {
            'get': mock_get,
            'post': mock_post,
            'put': mock_put,
            'delete': mock_delete
        }

@pytest.fixture
def dashboard(monkeypatch):
    # Mock Tk initialization
    monkeypatch.setattr(Tk, "__init__", lambda x: None)
    monkeypatch.setattr(Tk, "geometry", lambda x, y: None)
    monkeypatch.setattr(Tk, "title", lambda x, y: None)
    return ExpenseDashboard()

def test_fetch_expenses_success(dashboard, mock_api):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "expenses": [
            {
                "id": 1,
                "description": "Test expense",
                "amount": 100.00,
                "category": "test"
            }
        ]
    }
    mock_api['get'].return_value = mock_response

    # Act
    dashboard.fetch_expenses()

    # Assert
    assert len(dashboard.expenses) == 1
    assert dashboard.expenses[0]["description"] == "Test expense"
    mock_api['get'].assert_called_once()

def test_fetch_expenses_failure(dashboard, mock_api):
    # Arrange
    mock_api['get'].side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception):
        dashboard.fetch_expenses()

def test_edit_expense_success(dashboard, mock_api):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_api['put'].return_value = mock_response
    
    dashboard.expenses = [{"id": 1, "description": "Old desc"}]
    dashboard.expense_listbox = Mock()
    dashboard.expense_listbox.curselection.return_value = [0]

    # Act
    with patch('tkinter.simpledialog.askstring') as mock_dialog:
        mock_dialog.side_effect = ["New desc", "100", "test"]
        dashboard.edit_expense()

    # Assert
    mock_api['put'].assert_called_once()

def test_delete_expense_success(dashboard, mock_api):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_api['delete'].return_value = mock_response
    
    dashboard.expenses = [{"id": 1, "description": "Test"}]
    dashboard.expense_listbox = Mock()
    dashboard.expense_listbox.curselection.return_value = [0]

    # Act
    with patch('tkinter.messagebox.askyesno') as mock_dialog:
        mock_dialog.return_value = True
        dashboard.delete_expense()

    # Assert
    mock_api['delete'].assert_called_once()

def test_show_bar_chart(dashboard):
    # Arrange
    dashboard.expenses = [
        {"category": "test1", "amount": 100},
        {"category": "test2", "amount": 200}
    ]

    # Act & Assert
    with patch('matplotlib.pyplot') as mock_plt:
        dashboard.show_bar_chart()
        mock_plt.figure.assert_called_once()
        mock_plt.bar.assert_called_once()

def test_show_pie_chart(dashboard):
    # Arrange
    dashboard.expenses = [
        {"category": "test1", "amount": 100},
        {"category": "test2", "amount": 200}
    ]

    # Act & Assert
    with patch('matplotlib.pyplot') as mock_plt:
        dashboard.show_pie_chart()
        mock_plt.figure.assert_called_once()
        mock_plt.pie.assert_called_once()
