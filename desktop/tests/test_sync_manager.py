import pytest
import sqlite3
from unittest.mock import Mock, patch
from desktop.utils.sync_manager import SyncManager
from datetime import datetime

@pytest.fixture
def sync_manager():
    return SyncManager(database_path=":memory:")

@pytest.fixture
def sample_expense():
    return {
        "id": 1,
        "description": "Test expense",
        "amount": 100.00,
        "category": "test",
        "date": datetime.now().isoformat(),
        "synced": 0
    }

def test_setup_database(sync_manager):
    """Test database tables are created correctly"""
    conn = sqlite3.connect(sync_manager.database_path)
    cursor = conn.cursor()
    
    # Check sync_status table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_status'")
    assert cursor.fetchone() is not None
    
    # Check offline_queue table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='offline_queue'")
    assert cursor.fetchone() is not None

async def test_get_local_expenses(sync_manager, sample_expense):
    """Test fetching local expenses that need syncing"""
    # Setup
    conn = sqlite3.connect(sync_manager.database_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses
        (id INTEGER PRIMARY KEY, description TEXT, amount REAL, 
         category TEXT, synced INTEGER, modified_at TEXT)
    """)
    cursor.execute(
        "INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?)",
        (1, sample_expense["description"], sample_expense["amount"],
         sample_expense["category"], 0, datetime.now().isoformat())
    )
    conn.commit()

    # Test
    expenses = await sync_manager.get_local_expenses()
    assert len(expenses) == 1
    assert expenses[0]["description"] == sample_expense["description"]

async def test_queue_offline_operation(sync_manager):
    """Test queuing operations for later sync"""
    operation = "add_expense"
    data = {"amount": 100, "description": "Test"}
    
    await sync_manager.queue_offline_operation(operation, data)
    
    conn = sqlite3.connect(sync_manager.database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offline_queue")
    result = cursor.fetchone()
    
    assert result is not None
    assert operation in result[1]

async def test_update_sync_status(sync_manager):
    """Test updating sync status"""
    status = "completed"
    details = "Sync completed successfully"
    
    await sync_manager.update_sync_status(status, details)
    
    conn = sqlite3.connect(sync_manager.database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT status, details FROM sync_status WHERE id = 1")
    result = cursor.fetchone()
    
    assert result[0] == status
    assert result[1] == details
