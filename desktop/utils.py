from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import requests
import logging

# Configure Logging
logging.basicConfig(
    filename="utils.log",  # Log file for API calls and errors
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def handle_api_response(response):
    """
    Handle API responses and extract error messages if necessary.

    Args:
        response: requests.Response object from an API call.

    Returns:
        - Response JSON if successful.
        - None if an error occurred.
    """
    try:
        if response.status_code == 200:
            return response.json()
        else:
            error_message = response.json().get("error", "Unknown error occurred.")
            logging.error(f"API Error {response.status_code}: {error_message}")
            return None
    except Exception as e:
        logging.exception(f"Exception while handling API response: {e}")
        return None


def send_post_request(url, payload, headers=None):
    """
    Send a POST request to the given URL with the provided payload and optional custom headers.

    Args:
        url: Full API endpoint URL.
        payload: Dictionary containing the request body.
        headers: Optional dictionary for custom headers.

    Returns:
        - Response JSON if successful.
        - None if an error occurred.
    """
    try:
        # Include default headers and allow custom overrides
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)

        response = requests.post(url, json=payload, headers=default_headers)
        return handle_api_response(response)
    except Exception as e:
        logging.exception(f"Exception while sending POST request to {url}: {e}")
        return None


def send_get_request(url, headers=None):
    """
    Send a GET request to the given URL with optional custom headers.

    Args:
        url: Full API endpoint URL.
        headers: Optional dictionary for custom headers.

    Returns:
        - Response JSON if successful.
        - None if an error occurred.
    """
    try:
        # Include default headers and allow custom overrides
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)

        response = requests.get(url, headers=default_headers)
        return handle_api_response(response)
    except Exception as e:
        logging.exception(f"Exception while sending GET request to {url}: {e}")
        return None


def validate_input_fields(fields):
    """
    Validate required input fields.

    Args:
        fields: Dictionary where keys are field names and values are field values.

    Returns:
        True if all fields are filled, False otherwise.
    """
    for field_name, value in fields.items():
        if not value:
            logging.warning(f"Validation failed: {field_name} is empty.")
            return False
    return True
