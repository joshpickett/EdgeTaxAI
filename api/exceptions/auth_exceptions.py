class AuthenticationError(Exception):
    """Custom exception for authentication-related errors"""

    pass


class OTPError(Exception):
    """Custom exception for OTP-related errors"""

    pass


class RateLimitError(Exception):
    """Custom exception for rate limiting errors"""

    pass
