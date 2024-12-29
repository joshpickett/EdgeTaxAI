from marshmallow import ValidationError
from datetime import datetime
import re

def validate_tax_year(value):
    current_year = datetime.now().year
    if not (1900 <= value <= current_year + 1):
        raise ValidationError(f'Tax year must be between 1900 and {current_year + 1}')

def validate_amount(value):
    if value < 0:
        raise ValidationError('Amount cannot be negative')
    if len(str(value).split('.')[-1]) > 2:
        raise ValidationError('Amount cannot have more than 2 decimal places')

def validate_social_security_number(value):
    if not re.match(r'^\d{3}-?\d{2}-?\d{4}$', value):
        raise ValidationError('Invalid Social Security Number format')

def validate_employer_identification_number(value):
    if not re.match(r'^\d{2}-?\d{7}$', value):
        raise ValidationError('Invalid Employer Identification Number format')

def validate_phone_number(value):
    if not re.match(r'^\+?1?\d{10}$', value):
        raise ValidationError('Invalid phone number format')

def validate_zip_code(value):
    if not re.match(r'^\d{5}(-\d{4})?$', value):
        raise ValidationError('Invalid ZIP code format')
