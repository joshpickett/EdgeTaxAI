import pytest
from datetime import datetime, timedelta
from api.models.gig_data import GigData
from api.utils.gig_utils import process_platform_data


@pytest.fixture
def sample_trip_data():
    return {
        "user_id": 1,
        "platform": "uber",
        "trip_id": "test123",
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(minutes=30),
        "earnings": 25.50,
        "distance": 10.5,
        "status": "completed",
    }


@pytest.fixture
def sample_earnings_data():
    return {
        "user_id": 1,
        "platform": "uber",
        "period_start": datetime.now().date(),
        "period_end": (datetime.now() + timedelta(days=7)).date(),
        "gross_earnings": 750.00,
        "expenses": 150.00,
        "net_earnings": 600.00,
    }


def test_init_tables(tmp_path):
    """Test database initialization"""
    db_path = tmp_path / "test.db"
    gig_data = GigData(str(db_path))
    gig_data.init_tables()

    # Verify tables exist
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    assert "gig_trips" in tables
    assert "gig_earnings" in tables


def test_store_trip(tmp_path, sample_trip_data):
    """Test storing trip data"""
    db_path = tmp_path / "test.db"
    gig_data = GigData(str(db_path))
    gig_data.init_tables()

    trip_id = gig_data.store_trip(sample_trip_data)
    assert trip_id is not None

    # Verify stored data
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gig_trips WHERE id = ?", (trip_id,))
    stored_trip = cursor.fetchone()

    assert stored_trip is not None
    assert float(stored_trip[6]) == sample_trip_data["earnings"]


def test_store_earnings(tmp_path, sample_earnings_data):
    """Test storing earnings data"""
    db_path = tmp_path / "test.db"
    gig_data = GigData(str(db_path))
    gig_data.init_tables()

    earnings_id = gig_data.store_earnings(sample_earnings_data)
    assert earnings_id is not None

    # Verify stored data
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gig_earnings WHERE id = ?", (earnings_id,))
    stored_earnings = cursor.fetchone()

    assert stored_earnings is not None
    assert float(stored_earnings[5]) == sample_earnings_data["gross_earnings"]


def test_process_platform_data():
    """Test platform data processing"""
    raw_data = {
        "trips": [{"fare": 25.50, "distance": 10.5}, {"fare": 30.00, "distance": 12.0}],
        "period": "2023-01",
    }

    processed_data = process_platform_data("uber", raw_data)

    assert processed_data["platform"] == "uber"
    assert processed_data["earnings"] == 55.50
    assert len(processed_data["trips"]) == 2
