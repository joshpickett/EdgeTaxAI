import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from ..utils.sync_manager import SyncManager


@pytest.fixture
def sync_manager():
    return SyncManager()


@pytest.fixture
def mock_database():
    with patch("sqlite3.connect") as mock:
        yield mock


class TestSyncManager:
    @pytest.mark.asyncio
    async def test_sync_user_data_success(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor

        result = await sync_manager.sync_user_data("test_user")

        assert result["status"] == "success"
        assert "timestamp" in result
        assert "synced_items" in result

    @pytest.mark.asyncio
    async def test_sync_expenses(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": 200},
        ]

        result = await sync_manager.sync_expenses("test_user")

        assert result["status"] == "success"
        assert result["synced_count"] == 2

    @pytest.mark.asyncio
    async def test_sync_receipts(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"id": 1, "url": "receipt1.jpg"},
            {"id": 2, "url": "receipt2.jpg"},
        ]

        result = await sync_manager.sync_receipts("test_user")

        assert result["status"] == "success"
        assert result["synced_count"] == 2

    @pytest.mark.asyncio
    async def test_sync_platform_data(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"id": 1, "platform": "uber"},
            {"id": 2, "platform": "lyft"},
        ]

        result = await sync_manager.sync_platform_data("test_user")

        assert result["status"] == "success"
        assert "platform_results" in result

    @pytest.mark.asyncio
    async def test_sync_error_handling(self, sync_manager, mock_database):
        mock_database.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await sync_manager.sync_user_data("test_user")

    @pytest.mark.asyncio
    async def test_process_expense_sync(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor

        expense = {"id": 1, "amount": 100}
        await sync_manager._process_expense_sync(expense)

        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_receipt_sync(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor

        receipt = {"id": 1, "url": "receipt.jpg"}
        await sync_manager._process_receipt_sync(receipt)

        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_platform(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1, "data": "test_data"}]

        result = await sync_manager._sync_platform("test_user", "uber")

        assert result["status"] == "success"
        assert result["synced_count"] == 1

    @pytest.mark.asyncio
    async def test_process_platform_data_sync(self, sync_manager, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor

        platform_data = {"id": 1, "platform": "uber"}
        await sync_manager._process_platform_data_sync(platform_data)

        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()
