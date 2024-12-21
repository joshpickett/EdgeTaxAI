from typing import Dict, Any, Optional
import re
from datetime import datetime
from geopy.geocoders import Nominatim

class ValidationError(Exception):
    """Custom validation exception"""
    pass

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_platform(platform: str) -> bool:
    """Validate gig platform name"""
    valid_platforms = {'uber', 'lyft', 'doordash', 'instacart', 'upwork', 'fiverr'}
    return platform.lower() in valid_platforms

def validate_platform_data(data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Validate platform data structure"""
    errors = {}
    
    required_fields = ['platform', 'user_id', 'access_token']
    for field in required_fields:
        if field not in data:
            errors[field] = f"Missing required field: {field}"
            
    if errors:
        return errors
        
    return None

def validate_expense(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate expense data"""
    errors = {}
    
    if not data.get('amount'):
        errors['amount'] = 'Amount is required'
    elif not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        errors['amount'] = 'Amount must be a positive number'

    if not data.get('description'):
        errors['description'] = 'Description is required'
    elif len(data['description']) > 500:
        errors['description'] = 'Description too long'

    if errors:
        raise ValidationError(errors)

    return None

def validate_date(date_str: str) -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_location(location: str) -> bool:
    """
    Validate if a location string is valid using geocoding.
    """
    if not location or len(location.strip()) < 3:
        return False
        
    try:
        geolocator = Nominatim(user_agent="tax_edge_ai")
        location = geolocator.geocode(location)
        return location is not None
    except Exception:
        return False
