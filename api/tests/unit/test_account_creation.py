import pytest
from unittest.mock import Mock, patch
from api.account_creation import account_creation_page


@pytest.fixture
def mock_streamlit():
    with patch("streamlit.text_input") as mock_input, patch(
        "streamlit.button"
    ) as mock_button:
        yield {"text_input": mock_input, "button": mock_button}


@pytest.fixture
def mock_requests():
    with patch("requests.post") as mock_post:
        yield mock_post


def test_account_creation_valid_input(mock_streamlit, mock_requests):
    # Setup mock inputs
    mock_streamlit["text_input"].side_effect = [
        "test@example.com",  # email
        "+12345678900",  # phone
        "Password123!",  # password
    ]
    mock_streamlit["button"].return_value = True
    mock_requests.return_value.status_code = 201

    # Call the function
    account_creation_page("http://test-api")

    # Verify API call
    mock_requests.assert_called_once_with(
        "http://test-api/auth/signup",
        json={
            "email": "test@example.com",
            "phone": "+12345678900",
            "password": "Password123!",
        },
    )


def test_account_creation_invalid_email(mock_streamlit):
    mock_streamlit["text_input"].side_effect = [
        "invalid-email",
        "+12345678900",
        "Password123!",
    ]
    mock_streamlit["button"].return_value = True

    with pytest.raises(ValueError) as exc:
        account_creation_page("http://test-api")
    assert "Invalid email format" in str(exc.value)


def test_account_creation_missing_fields(mock_streamlit):
    mock_streamlit["text_input"].side_effect = [
        "",  # empty email
        "",  # empty phone
        "Password123!",
    ]
    mock_streamlit["button"].return_value = True

    with pytest.raises(ValueError) as exc:
        account_creation_page("http://test-api")
    assert "All fields are required" in str(exc.value)


def test_account_creation_api_error(mock_streamlit, mock_requests):
    mock_streamlit["text_input"].side_effect = [
        "test@example.com",
        "+12345678900",
        "Password123!",
    ]
    mock_streamlit["button"].return_value = True
    mock_requests.return_value.status_code = 500
    mock_requests.return_value.json.return_value = {"error": "Server error"}

    with pytest.raises(Exception) as exc:
        account_creation_page("http://test-api")
    assert "Server error" in str(exc.value)
