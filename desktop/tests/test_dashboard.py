import pytest
from unittest.mock import Mock, patch
import tkinter as tkinter
from datetime import datetime
from desktop.dashboard import ExpenseDashboard

@pytest.fixture
def mock_requests():
    with patch('desktop.dashboard.requests') as mock_request:
        yield mock_request

@pytest.fixture
def dashboard():
    with patch('tkinter.Tk'):
        return ExpenseDashboard()

@pytest.fixture
def sample_expenses():
    return {
        'expenses': [
            {
                'id': 1,
                'description': 'Test Expense',
                'amount': 100.00,
                'category': 'Test'
            }
        ]
    }

def test_fetch_expenses_success(dashboard, mock_requests, sample_expenses):
    """Test successful expense fetching"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = sample_expenses
    
    dashboard.fetch_expenses()
    
    assert len(dashboard.expenses) == 1
    mock_requests.get.assert_called_once()

def test_fetch_expenses_failure(dashboard, mock_requests):
    """Test expense fetching failure"""
    mock_requests.get.return_value.status_code = 400
    
    with patch('tkinter.messagebox.showerror') as mock_error:
        dashboard.fetch_expenses()
        mock_error.assert_called_once()

def test_edit_expense_success(dashboard, mock_requests):
    """Test successful expense editing"""
    dashboard.expenses = [{'id': 1, 'description': 'Old', 'amount': 50, 'category': 'Test'}]
    mock_requests.put.return_value.status_code = 200
    
    with patch('tkinter.simpledialog.askstring', return_value='New'):
        with patch('tkinter.simpledialog.askfloat', return_value=100.0):
            with patch('tkinter.messagebox.showinfo') as mock_info:
                dashboard.edit_expense()
                mock_info.assert_called_once()

def test_delete_expense_success(dashboard, mock_requests):
    """Test successful expense deletion"""
    dashboard.expenses = [{'id': 1, 'description': 'Test', 'amount': 50, 'category': 'Test'}]
    mock_requests.delete.return_value.status_code = 200
    
    with patch('tkinter.messagebox.askyesno', return_value=True):
        with patch('tkinter.messagebox.showinfo') as mock_info:
            dashboard.delete_expense()
            mock_info.assert_called_once()

def test_show_bar_chart(dashboard):
    """Test bar chart display"""
    dashboard.expenses = [
        {'category': 'Test1', 'amount': 100},
        {'category': 'Test2', 'amount': 200}
    ]
    
    with patch('matplotlib.pyplot') as mock_plt:
        dashboard.show_bar_chart()
        mock_plt.figure.assert_called_once()
        mock_plt.show.assert_called_once()

def test_show_pie_chart(dashboard):
    """Test pie chart display"""
    dashboard.expenses = [
        {'category': 'Test1', 'amount': 100},
        {'category': 'Test2', 'amount': 200}
    ]
    
    with patch('matplotlib.pyplot') as mock_plt:
        dashboard.show_pie_chart()
        mock_plt.figure.assert_called_once()
        mock_plt.show.assert_called_once()

def test_logout_success(dashboard, mock_requests):
    """Test successful logout"""
    mock_requests.post.return_value.status_code = 200
    
    with patch('tkinter.messagebox.showinfo') as mock_info:
        dashboard.logout()
        assert mock_info.call_count == 2

def test_logout_failure(dashboard, mock_requests):
    """Test logout with server notification failure"""
    mock_requests.post.return_value.status_code = 400
    
    with patch('tkinter.messagebox.showwarning') as mock_warning:
        dashboard.logout()
        mock_warning.assert_called_once()
