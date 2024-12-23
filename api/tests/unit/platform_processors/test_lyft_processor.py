import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.platform_processors.lyft_processor import LyftProcessor

@pytest.fixture
def lyft_processor():
    return LyftProcessor()

@pytest.fixture
def sample_ride_data():
    return {
        'rides': [
            {
                'ride_id': '456def',
                'started_at': '2023-01-01T10:00:00Z',
                'ended_at': '2023-01-01T10:30:00Z',
                'distance_miles': 12.5,
                'duration_seconds': 1800,
                'earnings': 28.50,
                'status': 'completed'
            }
        ]
    }

@pytest.fixture
def sample_earnings_data():
    return {
        'start_date': '2023-01-01',
        'end_date': '2023-01-07',
        'total_earnings': 800.00,
        'total_expenses': 160.00,
        'net_earnings': 640.00,
        'total_rides': 35
    }

@pytest.mark.asyncio
async def test_process_trips_success(lyft_processor, sample_ride_data):
    """Test successful processing of Lyft rides"""
    processed_trips = await lyft_processor.process_trips(sample_ride_data)
    
    assert len(processed_trips) == 1
    trip = processed_trips[0]
    assert trip['trip_id'] == '456def'
    assert trip['distance'] == 12.5
    assert trip['earnings'] == 28.50
    assert trip['platform'] == 'lyft'

@pytest.mark.asyncio
async def test_process_trips_empty_data(lyft_processor):
    """Test processing empty ride data"""
    processed_trips = await lyft_processor.process_trips({'rides': []})
    assert len(processed_trips) == 0

@pytest.mark.asyncio
async def test_process_trips_invalid_data(lyft_processor):
    """Test processing invalid ride data"""
    processed_trips = await lyft_processor.process_trips({})
    assert len(processed_trips) == 0

@pytest.mark.asyncio
async def test_process_earnings_success(lyft_processor, sample_earnings_data):
    """Test successful processing of Lyft earnings"""
    earnings = await lyft_processor.process_earnings(sample_earnings_data)
    
    assert earnings['platform'] == 'lyft'
    assert earnings['gross_earnings'] == 800.00
    assert earnings['net_earnings'] == 640.00
    assert earnings['rides_count'] == 35

@pytest.mark.asyncio
async def test_process_earnings_empty_data(lyft_processor):
    """Test processing empty earnings data"""
    earnings = await lyft_processor.process_earnings({})
    assert earnings == {}
