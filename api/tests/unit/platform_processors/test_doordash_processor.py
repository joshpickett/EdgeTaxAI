import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.platform_processors.doordash_processor import DoorDashProcessor

@pytest.fixture
def doordash_processor():
    return DoorDashProcessor()

@pytest.fixture
def sample_delivery_data():
    return {
        'deliveries': [
            {
                'delivery_id': '789ghi',
                'pickup_time': '2023-01-01T10:00:00Z',
                'delivery_time': '2023-01-01T10:30:00Z',
                'total_distance': 8.5,
                'total_time': 1800,
                'earnings': 15.50,
                'status': 'completed'
            }
        ]
    }

@pytest.fixture
def sample_earnings_data():
    return {
        'period_start': '2023-01-01',
        'period_end': '2023-01-07',
        'total_earnings': 500.00,
        'total_expenses': 100.00,
        'net_earnings': 400.00,
        'total_deliveries': 40
    }

@pytest.mark.asyncio
async def test_process_trips_success(doordash_processor, sample_delivery_data):
    """Test successful processing of DoorDash deliveries"""
    processed_trips = await doordash_processor.process_trips(sample_delivery_data)
    
    assert len(processed_trips) == 1
    trip = processed_trips[0]
    assert trip['trip_id'] == '789ghi'
    assert trip['distance'] == 8.5
    assert trip['earnings'] == 15.50
    assert trip['platform'] == 'doordash'

@pytest.mark.asyncio
async def test_process_trips_empty_data(doordash_processor):
    """Test processing empty delivery data"""
    processed_trips = await doordash_processor.process_trips({'deliveries': []})
    assert len(processed_trips) == 0

@pytest.mark.asyncio
async def test_process_trips_invalid_data(doordash_processor):
    """Test processing invalid delivery data"""
    processed_trips = await doordash_processor.process_trips({})
    assert len(processed_trips) == 0

@pytest.mark.asyncio
async def test_process_earnings_success(doordash_processor, sample_earnings_data):
    """Test successful processing of DoorDash earnings"""
    earnings = await doordash_processor.process_earnings(sample_earnings_data)
    
    assert earnings['platform'] == 'doordash'
    assert earnings['gross_earnings'] == 500.00
    assert earnings['net_earnings'] == 400.00
    assert earnings['deliveries_count'] == 40

@pytest.mark.asyncio
async def test_process_earnings_empty_data(doordash_processor):
    """Test processing empty earnings data"""
    earnings = await doordash_processor.process_earnings({})
    assert earnings == {}
