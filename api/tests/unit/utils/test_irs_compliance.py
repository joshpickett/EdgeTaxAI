import pytest
from decimal import Decimal
from api.utils.irs_compliance import IRSCompliance

@pytest.fixture
def irs_compliance():
    return IRSCompliance()

@pytest.fixture
def sample_expense():
    return {
        'category': 'meals',
        'amount': 100.00,
        'date': '2023-01-01',
        'receipt': True,
        'business_purpose': 'Client meeting',
        'attendees': ['John Doe', 'Jane Smith']
    }

def test_verify_compliance_success(irs_compliance, sample_expense):
    """Test successful compliance verification"""
    result = irs_compliance.verify_compliance(sample_expense)
    
    assert result['is_compliant'] is True
    assert result['compliance_score'] == 1.0
    assert result['missing_documentation'] == []
    assert result['deductible_amount'] == 50.00  # 50% of meals
    assert result['within_limits'] is True

def test_verify_compliance_missing_docs(irs_compliance):
    """Test compliance verification with missing documentation"""
    expense = {
        'category': 'meals',
        'amount': 100.00,
        'date': '2023-01-01'
    }
    
    result = irs_compliance.verify_compliance(expense)
    
    assert result['is_compliant'] is False
    assert result['compliance_score'] < 1.0
    assert len(result['missing_documentation']) > 0

def test_verify_compliance_over_limit(irs_compliance):
    """Test compliance verification with amount over limit"""
    expense = {
        'category': 'gifts',
        'amount': 50.00,  # Over $25 limit
        'date': '2023-01-01',
        'receipt': True,
        'business_purpose': 'Client gift'
    }
    
    result = irs_compliance.verify_compliance(expense)
    
    assert result['within_limits'] is False
    assert result['deductible_amount'] == 50.00

def test_verify_compliance_unknown_category(irs_compliance):
    """Test compliance verification with unknown category"""
    expense = {
        'category': 'unknown',
        'amount': 100.00
    }
    
    result = irs_compliance.verify_compliance(expense)
    
    assert result['is_compliant'] is True  # No specific requirements
    assert result['compliance_score'] == 1.0

def test_generate_audit_trail(irs_compliance, sample_expense):
    """Test audit trail generation"""
    audit_trail = irs_compliance.generate_audit_trail(sample_expense)
    
    assert audit_trail['timestamp'] == sample_expense['date']
    assert audit_trail['category'] == sample_expense['category']
    assert audit_trail['amount'] == sample_expense['amount']
    assert audit_trail['documentation']['receipt'] is True
    assert audit_trail['documentation']['purpose'] is True
    assert 'compliance_check' in audit_trail

def test_meals_deduction_calculation(irs_compliance):
    """Test meals deduction calculation"""
    expense = {
        'category': 'meals',
        'amount': 200.00,
        'receipt': True,
        'business_purpose': 'Team lunch',
        'attendees': ['Team A']
    }
    
    result = irs_compliance.verify_compliance(expense)
    assert result['deductible_amount'] == 100.00  # 50% of meals

def test_home_office_deduction_limit(irs_compliance):
    """Test home office deduction limit"""
    expense = {
        'category': 'home_office',
        'amount': 2000.00,
        'receipt': True,
        'business_purpose': 'Home office setup'
    }
    
    result = irs_compliance.verify_compliance(expense)
    assert result['within_limits'] is False
    assert result['deductible_amount'] == 2000.00

def test_compliance_rules_initialization(irs_compliance):
    """Test compliance rules initialization"""
    assert 'documentation_required' in irs_compliance.compliance_rules
    assert 'deduction_limits' in irs_compliance.compliance_rules
    assert isinstance(irs_compliance.compliance_rules['deduction_limits']['meals'], Decimal)

def test_empty_expense_handling(irs_compliance):
    """Test handling of empty expense data"""
    result = irs_compliance.verify_compliance({})
    
    assert result['is_compliant'] is True  # No specific requirements
    assert result['compliance_score'] == 1.0
    assert result['deductible_amount'] == 0.0
