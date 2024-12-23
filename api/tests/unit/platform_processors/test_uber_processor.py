import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.platform_processors.uber_processor import UberProcessor

@pytest.fixture
def uber_processor():
    return UberProcessor()

@pytest.fixture
def sample_trip_data():
    return {
        'trips': [
            {
                'uuid': '123abc',
                'pickup_time': '2023-01-01T10:00:00Z',
                'dropoff_time': '2023-01-01T10:30:00Z',
                'distance': 10.5,
                'duration': 1800,
                'fare_amount': 25.50,
                'status': 'completed'
            }
        ]
    }

@pytest.fixture
def sample_earnings_data():
    return {
        'period_start': '2023-01-01',
        'period_end': '2023-01-07',
        'earnings_total': 750.00,
        'expenses_total': 150.00,
        'net_earnings': 600.00,
        'trips_count': 30
    }

@pytest.mark.asyncio
async def test_process_trips_success(uber_processor, sample_trip_data):
    """Test successful processing of Uber trips"""
    processed_trips = await uber_processor.process_trips(sample_trip_data)
    
    assert len(processed_trips) == 1
    trip = processed_trips[0]
    assert trip['trip_id'] == '123abc'
    assert trip['distance'] == 10.5
    assert trip['earnings'] == 25.50
    assert trip['platform'] == 'uber'

@pytest.mark.asyncio
async def test_process_trips_empty_data(uber_processor):
    """Test processing empty trip data"""
    processed_trips = await uber_processor.process_trips({'trips': []})
    assert len(processed_trips) == 0

@pytest.mark.asyncio
async def test_process_trips_invalid_data(uber_processor):
    """Test processing invalid trip data"""
    processed_trips = await uber_processor.process_trips({})
    assert len(processed_trips) == 0

@pytest.mark.asyncio
async def test_process_earnings_success(uber_processor, sample_earnings_data):
    """Test successful processing of Uber earnings"""
    earnings = await uber_processor.process_earnings(sample_earnings_data)
    
    assert earnings['platform'] == 'uber'
    assert earnings['gross_earnings'] == 750.00
    assert earnings['net_earnings'] == 600.00
    assert earnings['trips_count'] == 30

@pytest.mark.asyncio
async def test_process_earnings_empty_data(uber_processor):
    """Test processing empty earnings data"""
    earnings = await uber_processor.process_earnings({})
    assert earnings == {}
