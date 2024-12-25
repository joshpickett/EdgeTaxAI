import pytest
from unittest.mock import Mock, patch
from desktop.services.sync_service_adapter import SyncServiceAdapter
from shared.constants import SYNC_STATES

@pytest.fixture
def sync_service():
    return SyncServiceAdapter(base_url="http://test-api")

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mock_sync_manager():
    with patch('desktop.services.sync_service_adapter.SyncManager') as mock:
        return mock

async def test_sync_data_success(sync_service, mock_requests, mock_sync_manager):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "completed"}
    mock_requests.return_value = mock_response

    # Act
    result = await sync_service.sync_data("test-user")

    # Assert
    assert result["status"] == "completed"
    mock_requests.assert_called_once()

async def test_sync_data_already_syncing(sync_service):
    # Arrange
    sync_service.sync_in_progress = True

    # Act
    result = await sync_service.sync_data("test-user")

    # Assert
    assert result["status"] == SYNC_STATES.SYNCING

async def test_sync_data_error(sync_service, mock_requests):
    # Arrange
    mock_requests.side_effect = Exception("Network error")

    # Act
    result = await sync_service.sync_data("test-user")

    # Assert
    assert result["status"] == "error"
    assert "Network error" in result["error"]

async def test_get_sync_status_success(sync_service, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "completed"}
    mock_requests.return_value = mock_response

    # Act
    result = await sync_service.get_sync_status("test-user")

    # Assert
    assert result["status"] == "completed"
