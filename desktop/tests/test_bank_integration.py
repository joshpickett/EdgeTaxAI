import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from datetime import date
from desktop.bank_integration import bank_integration_page

@pytest.fixture
def mock_streamlit():
    with patch('desktop.bank_integration.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('desktop.bank_integration.requests') as mock_requests:
        yield mock_requests

def test_bank_integration_unauthorized(mock_streamlit):
    """Test bank integration page when user is not logged in"""
    # Clear session state
    streamlit.session_state.clear()
    
    bank_integration_page()
    
    mock_streamlit.error.assert_called_once_with("Please log in to connect your bank accounts.")

def test_connect_bank_success(mock_streamlit, mock_requests):
    """Test successful bank connection"""
    streamlit.session_state["user_id"] = "123"
    mock_requests.post.return_value.status_code = 200
    mock_requests.post.return_value.json.return_value = {"link_token": "test_token"}
    
    with patch.object(mock_streamlit, 'button', return_value=True):
        bank_integration_page()
        
        mock_requests.post.assert_called_once()
        assert "link_token" in mock_requests.post.return_value.json()

def test_connect_bank_failure(mock_streamlit, mock_requests):
    """Test bank connection failure"""
    streamlit.session_state["user_id"] = "123"
    mock_requests.post.side_effect = Exception("Connection error")
    
    with patch.object(mock_streamlit, 'button', return_value=True):
        bank_integration_page()
        
        mock_streamlit.error.assert_called_with(
            "An unexpected error occurred while connecting to the bank."
        )

def test_fetch_transactions_success(mock_streamlit, mock_requests):
    """Test successful transaction fetching"""
    streamlit.session_state["user_id"] = "123"
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        "transactions": [
            {"id": 1, "amount": 100, "description": "Test"}
        ]
    }
    
    # Mock date inputs and button click
    with patch.object(mock_streamlit, 'date_input') as mock_date:
        mock_date.return_value = date(2023, 1, 1)
        with patch.object(mock_streamlit, 'button', return_value=True):
            bank_integration_page()
            
            mock_requests.get.assert_called_once()
            mock_streamlit.dataframe.assert_called_once()

def test_fetch_transactions_empty(mock_streamlit, mock_requests):
    """Test fetching transactions with empty result"""
    streamlit.session_state["user_id"] = "123"
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {"transactions": []}
    
    with patch.object(mock_streamlit, 'date_input') as mock_date:
        mock_date.return_value = date(2023, 1, 1)
        with patch.object(mock_streamlit, 'button', return_value=True):
            bank_integration_page()
            
            mock_streamlit.info.assert_called_with(
                "No transactions found for the connected accounts."
            )

def test_check_balances_success(mock_streamlit, mock_requests):
    """Test successful balance checking"""
    streamlit.session_state["user_id"] = "123"
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        "balances": [
            {
                "account_id": "acc123",
                "balance": 1000.00,
                "type": "checking"
            }
        ]
    }
    
    with patch.object(mock_streamlit, 'button', return_value=True):
        bank_integration_page()
        
        mock_requests.get.assert_called_once()
        assert mock_streamlit.write.call_count >= 3

def test_disconnect_bank_success(mock_streamlit, mock_requests):
    """Test successful bank disconnection"""
    streamlit.session_state["user_id"] = "123"
    mock_requests.post.return_value.status_code = 200
    
    with patch.object(mock_streamlit, 'button', return_value=True):
        with patch.object(mock_streamlit, 'confirm', return_value=True):
            bank_integration_page()
            
            mock_requests.post.assert_called_once()
            mock_streamlit.success.assert_called_with(
                "Bank account disconnected successfully"
            )
