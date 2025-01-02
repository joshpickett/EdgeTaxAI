import pytest
from unittest.mock import patch, MagicMock
from api.utils.gig_utils import PlatformAPI


@pytest.fixture
def mock_requests():
    with patch("requests.get") as mock_get:
        yield mock_get


def test_uber_trips_fetch(mock_requests):
    """Test Uber trips fetch"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "trips": [{"id": "1", "fare": 25.50}, {"id": "2", "fare": 30.00}]
    }
    mock_requests.return_value = mock_response

    api = PlatformAPI("uber", "test_token")
    result = api.fetch_trips("2023-01-01", "2023-01-31")

    assert len(result["trips"]) == 2
    assert result["trips"][0]["fare"] == 25.50


def test_lyft_trips_fetch(mock_requests):
    """Test Lyft trips fetch"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ride_history": [
            {"ride_id": "1", "earnings": 20.00},
            {"ride_id": "2", "earnings": 35.00},
        ]
    }
    mock_requests.return_value = mock_response

    api = PlatformAPI("lyft", "test_token")
    result = api.fetch_trips("2023-01-01", "2023-01-31")

    assert len(result["ride_history"]) == 2
    assert result["ride_history"][0]["earnings"] == 20.00


def test_doordash_trips_fetch(mock_requests):
    """Test DoorDash trips fetch"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "deliveries": [
            {"order_id": "1", "payout": 15.00},
            {"order_id": "2", "payout": 18.50},
        ]
    }
    mock_requests.return_value = mock_response

    api = PlatformAPI("doordash", "test_token")
    result = api.fetch_trips("2023-01-01", "2023-01-31")

    assert len(result["deliveries"]) == 2
    assert result["deliveries"][0]["payout"] == 15.00


def test_api_error_handling(mock_requests):
    """Test API error handling"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_requests.return_value = mock_response

    api = PlatformAPI("uber", "invalid_token")
    with pytest.raises(Exception) as exc_info:
        api.fetch_trips("2023-01-01", "2023-01-31")

    assert "Failed to fetch" in str(exc_info.value)
