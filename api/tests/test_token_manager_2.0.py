import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
from ..utils.token_manager import TokenManager


@pytest.fixture
def token_manager():
    return TokenManager()


@pytest.fixture
def mock_redis():
    with patch("redis.from_url") as mock:
        yield mock


class TestTokenManager:
    def test_check_token_expiry_expired(self, token_manager, mock_redis):
        expired_token = {
            "expires_at": (datetime.now() - timedelta(minutes=5)).isoformat()
        }
        mock_redis.return_value.get.return_value = json.dumps(expired_token)

        result = token_manager.check_token_expiry(123, "uber")
        assert result is True

    def test_check_token_expiry_valid(self, token_manager, mock_redis):
        valid_token = {"expires_at": (datetime.now() + timedelta(hours=1)).isoformat()}
        mock_redis.return_value.get.return_value = json.dumps(valid_token)

        result = token_manager.check_token_expiry(123, "uber")
        assert result is False

    def test_refresh_token_success(self, token_manager, mock_redis):
        new_tokens = {"access_token": "new_token", "expires_in": 3600}

        result = token_manager.refresh_token(123, "uber", new_tokens)
        assert result is True

    def test_refresh_token_failure(self, token_manager, mock_redis):
        mock_redis.return_value.setex.side_effect = Exception("Redis error")

        new_tokens = {"access_token": "new_token", "expires_in": 3600}

        result = token_manager.refresh_token(123, "uber", new_tokens)
        assert result is False

    def test_check_token_expiry_no_token(self, token_manager, mock_redis):
        mock_redis.return_value.get.return_value = None

        result = token_manager.check_token_expiry(123, "uber")
        assert result is True

    def test_refresh_token_with_custom_expiry(self, token_manager, mock_redis):
        new_tokens = {"access_token": "new_token", "expires_in": 7200}  # 2 hours

        result = token_manager.refresh_token(123, "uber", new_tokens)
        assert result is True

    def test_check_token_expiry_near_threshold(self, token_manager, mock_redis):
        near_expiry_token = {
            "expires_at": (datetime.now() + timedelta(minutes=4)).isoformat()
        }
        mock_redis.return_value.get.return_value = json.dumps(near_expiry_token)

        result = token_manager.check_token_expiry(123, "uber")
        assert result is True

    def test_refresh_token_invalid_data(self, token_manager, mock_redis):
        invalid_tokens = {"access_token": "new_token", "expires_in": "invalid"}

        result = token_manager.refresh_token(123, "uber", invalid_tokens)
        assert result is False

    def test_check_token_expiry_invalid_date(self, token_manager, mock_redis):
        invalid_token = {"expires_at": "invalid_date"}
        mock_redis.return_value.get.return_value = json.dumps(invalid_token)

        result = token_manager.check_token_expiry(123, "uber")
        assert result is True
