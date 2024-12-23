import pytest
from ...models.gig_data import GigData
from datetime import datetime, date

@pytest.fixture
def gig_data(test_db):
    """Initialize GigData with test database"""
    gig_data_instance = GigData("test_database.db")
    gig_data_instance.init_tables()
    return gig_data_instance

def test_store_trip(gig_data):
    """Test storing trip data"""
    trip_data = {
        "user_id": 1,
        "platform": "uber",
        "trip_id": "test123",
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "earnings": 25.50,
        "distance": 10.5,
        "status": "completed"
    }
    
    trip_id = gig_data.store_trip(trip_data)
    assert trip_id is not None
    assert isinstance(trip_id, int)

def test_store_earnings(gig_data):
    """Test storing earnings data"""
    earnings_data = {
        "user_id": 1,
        "platform": "uber",
        "period_start": date.today(),
        "period_end": date.today(),
        "gross_earnings": 100.00,
        "expenses": 20.00,
        "net_earnings": 80.00
    }
    
    earnings_id = gig_data.store_earnings(earnings_data)
    assert earnings_id is not None
    assert isinstance(earnings_id, int)

def test_update_sync_status(gig_data):
    """Test updating sync status"""
    result = gig_data.update_sync_status(
        user_id=1,
        platform="uber",
        status="completed"
    )
    assert result is True

def test_store_invalid_trip(gig_data):
    """Test storing invalid trip data"""
    invalid_trip = {
        "user_id": 1,
        # Missing required fields
    }
    
    trip_id = gig_data.store_trip(invalid_trip)
    assert trip_id is None

def test_store_duplicate_trip(gig_data):
    """Test handling duplicate trip entries"""
    trip_data = {
        "user_id": 1,
        "platform": "uber",
        "trip_id": "test123",
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "earnings": 25.50,
        "distance": 10.5,
        "status": "completed"
    }
    
    # First insertion should succeed
    first_id = gig_data.store_trip(trip_data)
    assert first_id is not None
    
    # Second insertion should fail
    second_id = gig_data.store_trip(trip_data)
    assert second_id is None
