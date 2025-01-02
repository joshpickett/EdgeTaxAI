import pytest
from unittest.mock import Mock
from ..utils.error_handler import (
    APIError,
    GigPlatformError,
    handle_plaid_error,
    handle_api_error,
    handle_platform_error,
)
from plaid.exceptions import PlaidError


class TestErrorHandler:
    def test_api_error_creation(self):
        error = APIError("Test error", 400, {"detail": "Additional info"})
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.payload == {"detail": "Additional info"}

    def test_gig_platform_error_creation(self):
        error = GigPlatformError("Platform error", "uber", "AUTH_FAILED", 401)
        assert error.message == "Platform error"
        assert error.platform == "uber"
        assert error.error_code == "AUTH_FAILED"
        assert error.status_code == 401

    def test_handle_plaid_error(self):
        mock_error = Mock(spec=PlaidError)
        mock_error.message = "Plaid API error"

        response, status_code = handle_plaid_error(mock_error)

        assert response.json["error"]["message"] == "Plaid API error"
        assert response.json["status"] == "error"
        assert status_code == 400

    def test_handle_api_error(self):
        error = APIError("API error", 500, {"source": "test"})
        response, status_code = handle_api_error(error)

        assert response.json["error"]["message"] == "API error"
        assert response.json["error"]["source"] == "test"
        assert status_code == 500

    def test_handle_platform_error_request_exception(self):
        error = Mock(spec=requests.exceptions.RequestException)
        response, status_code = handle_platform_error(error)

        assert response.json["error"] == "Platform API request failed"
        assert status_code == 503

    def test_handle_platform_error_token_error(self):
        error = TokenError("Token expired")
        response, status_code = handle_platform_error(error)

        assert response.json["error"] == "Token error"
        assert status_code == 401

    def test_handle_platform_error_value_error(self):
        error = ValueError("Invalid parameter")
        response, status_code = handle_platform_error(error)

        assert response.json["error"] == "Invalid request"
        assert status_code == 400

    def test_handle_platform_error_gig_platform_error(self):
        error = GigPlatformError("Platform error", "uber", "AUTH_FAILED")
        response, status_code = handle_platform_error(error)

        assert response.json["error"]["message"] == "Platform error"
        assert response.json["error"]["platform"] == "uber"
        assert response.json["error"]["error_code"] == "AUTH_FAILED"

    def test_error_chaining(self):
        try:
            raise APIError("Original error", 400)
        except APIError as e:
            response, status_code = handle_api_error(e)
            assert response.json["error"]["message"] == "Original error"
            assert status_code == 400

    def test_error_with_custom_payload(self):
        error = APIError(
            "Custom error",
            422,
            {
                "field_errors": {
                    "email": "Invalid email format",
                    "phone": "Invalid phone number",
                }
            },
        )
        response, status_code = handle_api_error(error)

        assert "field_errors" in response.json["error"]
        assert status_code == 422

    def test_nested_error_handling(self):
        try:
            try:
                raise ValueError("Base error")
            except ValueError as e:
                raise APIError("Wrapped error", 400) from e
        except APIError as e:
            response, status_code = handle_api_error(e)
            assert response.json["error"]["message"] == "Wrapped error"
            assert status_code == 400
