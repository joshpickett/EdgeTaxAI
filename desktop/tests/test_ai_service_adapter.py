import pytest
from unittest.mock import Mock, patch
from desktop.services.ai_service_adapter import AIServiceAdapter
from shared.services.taxService import TaxService


@pytest.fixture
def ai_service():
    return AIServiceAdapter()


@pytest.fixture
def mock_tax_service():
    with patch("shared.services.taxService.TaxService") as mock:
        yield mock


def test_categorize_expense_success(ai_service, mock_tax_service):
    # Arrange
    expense_data = {"description": "Uber ride to client", "amount": 25.50}
    expected_result = {"category": "transportation", "confidence": 0.95}
    mock_tax_service.analyzeTaxContext.return_value = expected_result

    # Act
    result = ai_service.categorize_expense(
        expense_data["description"], expense_data["amount"]
    )

    # Assert
    assert result == expected_result
    mock_tax_service.analyzeTaxContext.assert_called_once_with(
        expense_data["description"], expense_data["amount"]
    )


def test_categorize_expense_error(ai_service, mock_tax_service):
    # Arrange
    mock_tax_service.analyzeTaxContext.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc:
        ai_service.categorize_expense("test", 100)
    assert str(exc.value) == "API Error"


@pytest.mark.asyncio
async def test_analyze_receipt_success(ai_service, mock_tax_service):
    # Arrange
    receipt_text = "Test receipt content"
    expected_result = {
        "total": 125.50,
        "items": [
            {"description": "Item 1", "amount": 25.50},
            {"description": "Item 2", "amount": 100.00},
        ],
    }
    mock_tax_service.analyzeReceipt.return_value = expected_result

    # Act
    result = await ai_service.analyze_receipt(receipt_text)

    # Assert
    assert result == expected_result
    mock_tax_service.analyzeReceipt.assert_called_once_with(receipt_text)


@pytest.mark.asyncio
async def test_analyze_receipt_error(ai_service, mock_tax_service):
    # Arrange
    mock_tax_service.analyzeReceipt.side_effect = Exception("OCR Error")

    # Act & Assert
    with pytest.raises(Exception) as exc:
        await ai_service.analyze_receipt("test receipt")
    assert str(exc.value) == "OCR Error"


def test_get_tax_suggestions_success(ai_service, mock_tax_service):
    # Arrange
    expense_data = {"description": "Office supplies", "amount": 150.00}
    expected_result = {
        "deductible": True,
        "category": "office_supplies",
        "confidence": 0.9,
    }
    mock_tax_service.getOptimizationSuggestions.return_value = expected_result

    # Act
    result = ai_service.get_tax_suggestions(expense_data)

    # Assert
    assert result == expected_result
    mock_tax_service.getOptimizationSuggestions.assert_called_once_with(expense_data)
