import pytest
from unittest.mock import Mock, patch
from desktop.bank_integration import bank_integration_page


@pytest.fixture
def mock_streamlit():
    with patch("streamlit.title") as mock_title, patch(
        "streamlit.markdown"
    ) as mock_markdown, patch("streamlit.button") as mock_button, patch(
        "streamlit.error"
    ) as mock_error, patch(
        "streamlit.success"
    ) as mock_success:
        yield {
            "title": mock_title,
            "markdown": mock_markdown,
            "button": mock_button,
            "error": mock_error,
            "success": mock_success,
        }


@pytest.fixture
def mock_bank_service():
    with patch("desktop.services.bank_service_adapter.BankServiceAdapter") as mock:
        return mock


@pytest.fixture
def mock_ai_service():
    with patch("desktop.services.ai_service_adapter.AIServiceAdapter") as mock:
        return mock


def test_bank_integration_unauthorized(mock_streamlit):
    """Test unauthorized access"""
    bank_integration_page()
    mock_streamlit["error"].assert_called_once_with(
        "Please log in to connect your bank accounts."
    )


def test_connect_bank_success(mock_streamlit, mock_bank_service):
    """Test successful bank connection"""
    # Setup
    mock_streamlit["button"].return_value = True
    mock_bank_service.get_link_token.return_value = "test-token"

    # Execute
    bank_integration_page()

    # Verify
    mock_bank_service.get_link_token.assert_called_once()
    mock_streamlit["success"].assert_called_once()


def test_connect_bank_failure(mock_streamlit, mock_bank_service):
    """Test failed bank connection"""
    # Setup
    mock_streamlit["button"].return_value = True
    mock_bank_service.get_link_token.side_effect = Exception("Connection failed")

    # Execute
    bank_integration_page()

    # Verify
    mock_streamlit["error"].assert_called_with(
        "An unexpected error occurred while connecting to the bank."
    )


def test_fetch_transactions_success(mock_streamlit, mock_bank_service, mock_ai_service):
    """Test successful transaction fetch"""
    # Setup
    mock_transactions = [{"description": "Test transaction", "amount": 100.00}]
    mock_bank_service.get_transactions.return_value = mock_transactions
    mock_ai_service.categorize_expense.return_value = {"category": "test"}

    # Execute
    bank_integration_page()

    # Verify
    mock_bank_service.get_transactions.assert_called_once()
    mock_ai_service.categorize_expense.assert_called_once()


def test_fetch_transactions_failure(mock_streamlit, mock_bank_service):
    """Test failed transaction fetch"""
    # Setup
    mock_bank_service.get_transactions.side_effect = Exception("Fetch failed")

    # Execute
    bank_integration_page()

    # Verify
    mock_streamlit["error"].assert_called_with(
        "An unexpected error occurred while fetching transactions."
    )


def test_check_balances_success(mock_streamlit, mock_bank_service):
    """Test successful balance check"""
    # Setup
    mock_balances = [{"account_id": "test", "balance": 1000.00, "type": "checking"}]
    mock_bank_service.get_balances.return_value = mock_balances

    # Execute
    bank_integration_page()

    # Verify
    mock_bank_service.get_balances.assert_called_once()
    mock_streamlit["success"].assert_called_once()


def test_check_balances_failure(mock_streamlit, mock_bank_service):
    """Test failed balance check"""
    # Setup
    mock_bank_service.get_balances.side_effect = Exception("Balance check failed")

    # Execute
    bank_integration_page()

    # Verify
    mock_streamlit["error"].assert_called_with("Error checking balances")
