import pytest
from api.utils.tax_calculator import TaxCalculator

@pytest.fixture
def tax_calculator():
    return TaxCalculator()

@pytest.fixture
def sample_expenses():
    return [
        {'amount': 100.0, 'category': 'fuel'},
        {'amount': 200.0, 'category': 'maintenance'}
    ]

def test_calculate_mileage_deduction(tax_calculator):
    """Test mileage deduction calculation"""
    miles = 1000
    expected = miles * tax_calculator.standard_mileage_rate
    result = tax_calculator.calculate_mileage_deduction(miles)
    
    assert result == round(expected, 2)
    assert isinstance(result, float)

def test_calculate_self_employment_tax(tax_calculator):
    """Test self-employment tax calculation"""
    net_income = 50000
    result = tax_calculator.calculate_self_employment_tax(net_income)
    
    assert 'tax_amount' in result
    assert 'tax_rate' in result
    assert result['tax_rate'] == 0.153
    assert result['tax_amount'] == round(net_income * 0.153, 2)

def test_calculate_income_tax(tax_calculator):
    """Test income tax calculation"""
    taxable_income = 50000
    result = tax_calculator.calculate_income_tax(taxable_income)
    
    assert 'tax_amount' in result
    assert 'effective_rate' in result
    assert result['tax_amount'] > 0
    assert 0 < result['effective_rate'] < 1

def test_estimate_quarterly_taxes(tax_calculator):
    """Test quarterly tax estimation"""
    result = tax_calculator.estimate_quarterly_taxes(
        income=100000,
        expenses=20000,
        mileage=5000
    )
    
    assert 'quarterly_payment' in result
    assert 'annual_tax_estimate' in result
    assert 'self_employment_tax' in result
    assert 'income_tax' in result
    assert 'total_deductions' in result
    assert result['quarterly_payment'] == round(result['annual_tax_estimate'] / 4, 2)

def test_get_tax_summary(tax_calculator, sample_expenses):
    """Test comprehensive tax summary generation"""
    result = tax_calculator.get_tax_summary(
        annual_income=100000,
        expenses=sample_expenses,
        mileage=5000
    )
    
    assert 'gross_income' in result
    assert 'total_expenses' in result
    assert 'mileage_deduction' in result
    assert 'net_income' in result
    assert 'quarterly_tax_payments' in result
    assert 'annual_tax_estimate' in result
    assert 'effective_tax_rate' in result

def test_zero_income_handling(tax_calculator):
    """Test handling of zero income"""
    result = tax_calculator.get_tax_summary(0, [], 0)
    
    assert result['gross_income'] == 0
    assert result['net_income'] == 0
    assert result['effective_tax_rate'] == 0

def test_negative_income_handling(tax_calculator):
    """Test handling of negative net income"""
    result = tax_calculator.estimate_quarterly_taxes(
        income=10000,
        expenses=15000,
        mileage=1000
    )
    
    assert result['quarterly_payment'] == 0
    assert result['annual_tax_estimate'] == 0

def test_tax_bracket_progression(tax_calculator):
    """Test tax calculation across different brackets"""
    incomes = [20000, 50000, 100000, 200000]
    effective_rates = []
    
    for income in incomes:
        result = tax_calculator.calculate_income_tax(income)
        effective_rates.append(result['effective_rate'])
    
    # Verify progressive nature of tax rates
    assert all(effective_rates[i] <= effective_rates[i+1] 
              for i in range(len(effective_rates)-1))

def test_mileage_deduction_zero_miles(tax_calculator):
    """Test mileage deduction with zero miles"""
    result = tax_calculator.calculate_mileage_deduction(0)
    assert result == 0

def test_high_income_tax_calculation(tax_calculator):
    """Test tax calculation for high income"""
    result = tax_calculator.calculate_income_tax(1000000)
    assert result['effective_rate'] > 0.3  # Should be in highest bracket
