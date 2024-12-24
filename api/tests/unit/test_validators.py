import pytest
from api.utils.validators import (
    validate_email, validate_phone, validate_platform,
    validate_platform_data, validate_expense, validate_date,
    validate_location, ValidationError
)

def test_validate_email_success():
    """Test valid email validation"""
    assert validate_email('test@example.com') is True
    assert validate_email('user.name+tag@domain.co.uk') is True

def test_validate_email_failure():
    """Test invalid email validation"""
    assert validate_email('invalid.email') is False
    assert validate_email('@domain.com') is False
    assert validate_email('user@') is False

def test_validate_phone_success():
    """Test valid phone number validation"""
    assert validate_phone('+12345678901') is True
    assert validate_phone('12345678901') is True

def test_validate_phone_failure():
    """Test invalid phone number validation"""
    assert validate_phone('123') is False
    assert validate_phone('abcdefghijk') is False

def test_validate_platform_success():
    """Test valid platform validation"""
    assert validate_platform('uber') is True
    assert validate_platform('LYFT') is True
    assert validate_platform('doordash') is True

def test_validate_platform_failure():
    """Test invalid platform validation"""
    assert validate_platform('invalid_platform') is False
    assert validate_platform('') is False

def test_validate_platform_data_success():
    """Test valid platform data validation"""
    data = {
        'platform': 'uber',
        'user_id': 1,
        'access_token': 'token123'
    }
    assert validate_platform_data(data) is None

def test_validate_platform_data_failure():
    """Test invalid platform data validation"""
    data = {
        'platform': 'uber',
        'user_id': 1
    }
    errors = validate_platform_data(data)
    assert 'access_token' in errors

def test_validate_expense_success():
    """Test valid expense validation"""
    data = {
        'amount': 100.50,
        'description': 'Test expense'
    }
    assert validate_expense(data) is None

def test_validate_expense_failure():
    """Test invalid expense validation"""
    data = {
        'amount': -100,
        'description': 'Test expense'
    }
    with pytest.raises(ValidationError) as exc_info:
        validate_expense(data)
    assert 'amount' in str(exc_info.value)

def test_validate_date_success():
    """Test valid date validation"""
    assert validate_date('2023-01-01') is True

def test_validate_date_failure():
    """Test invalid date validation"""
    assert validate_date('2023/01/01') is False
    assert validate_date('invalid_date') is False

@pytest.mark.asyncio
async def test_validate_location_success():
    """Test valid location validation"""
    with patch('geopy.geocoders.Nominatim.geocode') as mock_geocode:
        mock_geocode.return_value = Mock(latitude=40.7128, longitude=-74.0060)
        assert validate_location('New York, NY') is True

@pytest.mark.asyncio
async def test_validate_location_failure():
    """Test invalid location validation"""
    with patch('geopy.geocoders.Nominatim.geocode') as mock_geocode:
        mock_geocode.return_value = None
        assert validate_location('Invalid Location XYZ') is False
