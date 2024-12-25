import pytest
from datetime import datetime
from api.utils.validators import (
    validate_email, validate_phone, validate_platform,
    validate_platform_data, validate_expense, validate_date,
    validate_location, ValidationError
)

def test_validate_email_valid():
    assert validate_email("test@example.com") == True
    assert validate_email("user.name+tag@domain.co.uk") == True
    assert validate_email("test.email-123@sub.domain.com") == True

def test_validate_email_invalid():
    assert validate_email("invalid.email") == False
    assert validate_email("@domain.com") == False
    assert validate_email("user@") == False
    assert validate_email("") == False
    assert validate_email("no spaces@domain.com") == False

def test_validate_phone_valid():
    assert validate_phone("+12345678900") == True
    assert validate_phone("12345678900") == True
    assert validate_phone("+44123456789") == True

def test_validate_phone_invalid():
    assert validate_phone("123") == False
    assert validate_phone("abcdefghijk") == False
    assert validate_phone("") == False
    assert validate_phone("+1234") == False
    assert validate_phone("123-456-7890") == False

def test_validate_platform_valid():
    assert validate_platform("uber") == True
    assert validate_platform("UBER") == True
    assert validate_platform("lyft") == True
    assert validate_platform("doordash") == True

def test_validate_platform_invalid():
    assert validate_platform("invalid_platform") == False
    assert validate_platform("") == False
    assert validate_platform("uber ") == False
    assert validate_platform("123") == False

def test_validate_platform_data_valid():
    data = {
        "platform": "uber",
        "user_id": "123",
        "access_token": "token123"
    }
    assert validate_platform_data(data) is None

def test_validate_platform_data_missing_fields():
    data = {
        "platform": "uber",
        "user_id": "123"
    }
    errors = validate_platform_data(data)
    assert "access_token" in errors
    assert errors["access_token"] == "Missing required field: access_token"

def test_validate_platform_data_empty_fields():
    data = {
        "platform": "",
        "user_id": "",
        "access_token": ""
    }
    errors = validate_platform_data(data)
    assert len(errors) > 0

def test_validate_expense_valid():
    data = {
        "amount": 100.50,
        "description": "Test expense"
    }
    assert validate_expense(data) is None

def test_validate_expense_missing_amount():
    with pytest.raises(ValidationError) as exc:
        validate_expense({"description": "Test"})
    assert "amount" in str(exc.value)

def test_validate_expense_invalid_amount():
    with pytest.raises(ValidationError) as exc:
        validate_expense({"amount": -50, "description": "Test"})
    assert "amount" in str(exc.value)

def test_validate_expense_missing_description():
    with pytest.raises(ValidationError) as exc:
        validate_expense({"amount": 100})
    assert "description" in str(exc.value)

def test_validate_date_valid():
    assert validate_date("2023-01-01") == True
    assert validate_date("2023-12-31") == True
    assert validate_date("2024-02-29") == True

def test_validate_date_invalid():
    assert validate_date("2023/01/01") == False
    assert validate_date("invalid-date") == False
    assert validate_date("") == False
    assert validate_date("2023-13-01") == False
    assert validate_date("2023-01-32") == False

@pytest.mark.asyncio
async def test_validate_location_valid(mocker):
    mock_geocode = mocker.patch('geopy.geocoders.Nominatim.geocode')
    mock_geocode.return_value = mocker.Mock()
    
    assert await validate_location("New York, NY") == True
    assert await validate_location("123 Main St, Boston, MA") == True
    mock_geocode.assert_called()

@pytest.mark.asyncio
async def test_validate_location_invalid(mocker):
    mock_geocode = mocker.patch('geopy.geocoders.Nominatim.geocode')
    mock_geocode.return_value = None
    
    assert await validate_location("") == False
    assert await validate_location("ab") == False
    assert await validate_location("Invalid Location XYZ") == False
    
@pytest.mark.asyncio
async def test_validate_location_error(mocker):
    mock_geocode = mocker.patch('geopy.geocoders.Nominatim.geocode')
    mock_geocode.side_effect = Exception("Geocoding error")
    
    assert await validate_location("New York, NY") == False
