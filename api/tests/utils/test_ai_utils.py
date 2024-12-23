import pytest
from unittest.mock import patch, MagicMock
from ....utils.ai_utils import (
    categorize_expense,
    analyze_tax_context,
    analyze_expense_patterns,
    verify_irs_compliance
)

@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses"""
    with patch('api.utils.ai_utils.client') as mock_client:
        yield mock_client

def test_categorize_expense(mock_openai):
    """Test expense categorization"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "travel|0.95|business trip|true"
    mock_openai.chat.completions.create.return_value = mock_response
    
    result = categorize_expense("Flight to conference")
    
    assert result['category'] == 'travel'
    assert result['confidence'] == 0.95
    assert result['tax_deductible'] == 'true'

def test_analyze_tax_context():
    """Test tax context analysis"""
    result = analyze_tax_context("Office supplies purchase", 100.0)
    
    assert 'context' in result
    assert 'confidence' in result
    assert 'suggested_category' in result
    assert 'deductible_amount' in result

def test_analyze_expense_patterns():
    """Test expense pattern analysis"""
    expenses = [
        {
            'description': 'Gas station',
            'amount': 50.0,
            'category': 'vehicle',
            'date': '2023-01-01'
        },
        {
            'description': 'Office supplies',
            'amount': 75.0,
            'category': 'office',
            'date': '2023-01-02'
        }
    ]
    
    patterns = analyze_expense_patterns(expenses)
    
    assert 'frequency' in patterns
    assert 'amount' in patterns
    assert 'time' in patterns
    assert 'location' in patterns

def test_verify_irs_compliance():
    """Test IRS compliance verification"""
    expense_data = {
        'description': 'Business lunch',
        'amount': 50.0,
        'date': '2023-01-01',
        'receipt': 'receipt.jpg',
        'tax_context': {'context': 'business'}
    }
    
    result = verify_irs_compliance(expense_data)
    
    assert result['is_compliant'] is True
    assert 'compliance_score' in result
    assert 'missing_fields' in result
