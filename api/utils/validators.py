from typing import Dict, Any


class ValidationError(Exception):
    pass


def validate_login_input(data: Dict[str, Any]) -> None:
    """Validate login input data"""
    if not data.get("email") and not data.get("phone_number"):
        raise ValidationError("Either email or phone number is required")

    if data.get("email") and not is_valid_email(data["email"]):
        raise ValidationError("Invalid email format")

    if data.get("phone_number") and not is_valid_phone(data["phone_number"]):
        raise ValidationError("Invalid phone number format")
