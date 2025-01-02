import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from ..gig_platform_service import (
    get_oauth_link,
    fetch_connected_platforms,
    fetch_platform_data,
    handle_oauth_callback,
    validate_platform_connection,
    disconnect_platform,
    PlatformStatus,
)


def test_get_oauth_link(mock_requests):
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_requests(
            json_data={"oauth_url": "http://test-oauth.com"}
        )

        result = get_oauth_link("uber", "http://callback")
        assert result == "http://test-oauth.com"
        mock_get.assert_called_once()


def test_fetch_connected_platforms(mock_requests, mock_platform_data):
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_requests(
            json_data={"connected_accounts": mock_platform_data["connected_accounts"]}
        )

        result = fetch_connected_platforms(123)
        assert len(result) == 1
        assert result[0]["platform"] == "uber"


def test_fetch_platform_data_success(mock_requests, mock_platform_data):
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_requests(json_data=mock_platform_data)

        result = fetch_platform_data(123, "uber")
        assert result["earnings"] == 1000.00
        assert len(result["trips"]) == 1


def test_handle_oauth_callback(mock_requests, mock_token_storage):
    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_requests(
            json_data={"token_data": {"access_token": "test"}}
        )

        result = handle_oauth_callback("test_code", "uber", 123)
        assert result == True


def test_validate_platform_connection(mock_requests):
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_requests(
            json_data={"connected": True, "last_sync": datetime.now().isoformat()}
        )

        result = validate_platform_connection(123, "uber")
        assert isinstance(result, PlatformStatus)
        assert result.connected == True


def test_disconnect_platform(mock_requests):
    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_requests(status_code=200)

        result = disconnect_platform(123, "uber")
        assert result == True


def test_retry_mechanism():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            {"status": "success"},
        ]

        # Test that function retries specified number of times
        with pytest.raises(Exception):
            fetch_connected_platforms(123)
        assert mock_get.call_count == 3
