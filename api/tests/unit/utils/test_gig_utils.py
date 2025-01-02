import pytest
from unittest.mock import patch, Mock
from api.utils.gig_utils import (
    get_oauth_url,
    exchange_code_for_token,
    store_platform_data,
    get_connected_accounts,
    fetch_access_token,
    PlatformAPI,
)


@pytest.fixture
def mock_env_vars():
    with patch.dict(
        "os.environ",
        {
            "UBER_CLIENT_ID": "test_client_id",
            "UBER_REDIRECT_URI": "test_redirect_uri",
            "UBER_CLIENT_SECRET": "test_client_secret",
        },
    ):
        yield


def test_get_oauth_url(mock_env_vars):
    """Test OAuth URL generation"""
    url = get_oauth_url("uber")
    assert "test_client_id" in url
    assert "test_redirect_uri" in url
    assert "scope" in url


def test_get_oauth_url_invalid_platform():
    """Test OAuth URL generation for invalid platform"""
    url = get_oauth_url("invalid_platform")
    assert url is None


@patch("requests.post")
def test_exchange_code_for_token(mock_post, mock_env_vars):
    """Test token exchange"""
    mock_post.return_value.json.return_value = {"access_token": "test_token"}
    result = exchange_code_for_token("uber", "test_code")
    assert result["access_token"] == "test_token"
    mock_post.assert_called_once()


@patch("sqlite3.connect")
def test_store_platform_data(mock_connect):
    """Test platform data storage"""
    mock_cursor = Mock()
    mock_connect.return_value.cursor.return_value = mock_cursor

    token_data = {"access_token": "test_token", "refresh_token": "refresh_token"}
    store_platform_data(1, "uber", token_data)

    mock_cursor.execute.assert_called_once()
    mock_connect.return_value.commit.assert_called_once()


@patch("sqlite3.connect")
def test_get_connected_accounts(mock_connect):
    """Test fetching connected accounts"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [("uber",), ("lyft",)]
    mock_connect.return_value.cursor.return_value = mock_cursor

    accounts = get_connected_accounts(1)
    assert len(accounts) == 2
    assert accounts[0]["platform"] == "uber"


@patch("sqlite3.connect")
def test_fetch_access_token(mock_connect):
    """Test access token retrieval"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = ("test_token",)
    mock_connect.return_value.cursor.return_value = mock_cursor

    token = fetch_access_token(1, "uber")
    assert token == "test_token"


class TestPlatformAPI:
    @pytest.fixture
    def platform_api(self):
        return PlatformAPI("uber", "test_token")

    @patch("requests.get")
    def test_fetch_earnings(self, mock_get, platform_api):
        """Test earnings fetch"""
        mock_get.return_value.json.return_value = {"earnings": 100}
        result = platform_api.fetch_earnings("2023-01-01", "2023-01-31")
        assert mock_get.called
        assert "earnings" in result

    @patch("requests.get")
    def test_fetch_trips(self, mock_get, platform_api):
        """Test trips fetch"""
        mock_get.return_value.json.return_value = {"trips": []}
        result = platform_api.fetch_trips("2023-01-01", "2023-01-31")
        assert mock_get.called
        assert "trips" in result

    def test_invalid_platform(self):
        """Test invalid platform handling"""
        with pytest.raises(ValueError):
            PlatformAPI("invalid_platform", "test_token")

    @patch("requests.get")
    def test_api_error_handling(self, mock_get, platform_api):
        """Test API error handling"""
        mock_get.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            platform_api.fetch_trips("2023-01-01", "2023-01-31")
