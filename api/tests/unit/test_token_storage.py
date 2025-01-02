import pytest
import jwt
from datetime import datetime, timedelta
from api.utils.token_storage import TokenStorage


@pytest.fixture
def token_storage():
    return TokenStorage("test_secret_key")


def test_generate_token_success(token_storage):
    user_id = 123
    token = token_storage.generate_token(user_id)
    assert token is not None

    # Verify token contents
    decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    assert decoded["user_id"] == user_id
    assert "exp" in decoded
    assert "iat" in decoded


def test_generate_token_with_claims(token_storage):
    user_id = 123
    additional_claims = {"role": "admin", "platform": "web"}
    token = token_storage.generate_token(user_id, additional_claims)

    decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    assert decoded["role"] == "admin"
    assert decoded["platform"] == "web"


def test_verify_token_valid(token_storage):
    user_id = 123
    token = token_storage.generate_token(user_id)

    is_valid, claims = token_storage.verify_token(token)
    assert is_valid
    assert claims["user_id"] == user_id


def test_verify_token_expired(token_storage):
    user_id = 123
    token = jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=2),
        },
        "test_secret_key",
        algorithm="HS256",
    )

    is_valid, claims = token_storage.verify_token(token)
    assert not is_valid
    assert claims["error"] == "Token expired"


def test_verify_token_invalid(token_storage):
    is_valid, claims = token_storage.verify_token("invalid_token")
    assert not is_valid
    assert claims["error"] == "Invalid token"


def test_store_token_success(token_storage, mocker):
    mock_keyring = mocker.patch("keyring.set_password")
    user_id = 123
    token = "test_token"

    result = token_storage.store_token(user_id, token)
    assert result
    mock_keyring.assert_called_once()


def test_retrieve_token_success(token_storage, mocker):
    mock_keyring = mocker.patch("keyring.get_password", return_value="test_token")
    user_id = 123

    token = token_storage.retrieve_token(user_id)
    assert token == "test_token"
    mock_keyring.assert_called_once()


def test_retrieve_token_failure(token_storage, mocker):
    mock_keyring = mocker.patch(
        "keyring.get_password", side_effect=Exception("Storage error")
    )
    user_id = 123

    token = token_storage.retrieve_token(user_id)
    assert token is None
