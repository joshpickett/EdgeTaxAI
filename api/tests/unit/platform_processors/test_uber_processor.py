import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from api.utils.platform_processors.uber_processor import UberProcessor


@pytest.fixture
def uber_processor():
    return UberProcessor()


@pytest.fixture
def mock_api_response():
    return {
        "trips": [
            {
                "id": "123",
                "start_time": "2023-01-01T10:00:00Z",
                "end_time": "2023-01-01T10:30:00Z",
                "distance": 10.5,
                "fare": 25.50,
                "status": "completed",
            }
        ],
        "earnings": {"total": 150.00, "trips_count": 5},
    }


@pytest.mark.asyncio
async def test_process_trips_success(uber_processor, mock_api_response):
    """Test successful processing of Uber trips"""
    processed_trips = await uber_processor.process_trips(mock_api_response)

    assert len(processed_trips) == 1
    trip = processed_trips[0]
    assert trip["trip_id"] == "123"
    assert trip["distance"] == 10.5
    assert trip["earnings"] == 25.50
    assert trip["platform"] == "uber"


@pytest.mark.asyncio
async def test_process_trips_empty_data(uber_processor):
    """Test processing empty trip data"""
    processed_trips = await uber_processor.process_trips({"trips": []})
    assert len(processed_trips) == 0


@pytest.mark.asyncio
async def test_process_trips_invalid_data(uber_processor):
    """Test processing invalid trip data"""
    processed_trips = await uber_processor.process_trips({})
    assert len(processed_trips) == 0


@pytest.mark.asyncio
async def test_process_earnings_success(uber_processor, mock_api_response):
    """Test successful processing of Uber earnings"""
    earnings = await uber_processor.process_earnings(mock_api_response)

    assert earnings["platform"] == "uber"
    assert earnings["total_earnings"] == 150.00
    assert earnings["trips_count"] == 5


@pytest.mark.asyncio
async def test_process_earnings_empty_data(uber_processor):
    """Test processing empty earnings data"""
    earnings = await uber_processor.process_earnings({})
    assert earnings == {}


@pytest.mark.asyncio
async def test_validate_trip_data(uber_processor, mock_api_response):
    """Test trip data validation"""
    trip = mock_api_response["trips"][0]
    is_valid = uber_processor._validate_trip_data(trip)
    assert is_valid is True


@pytest.mark.asyncio
async def test_validate_trip_data_invalid(uber_processor):
    """Test invalid trip data validation"""
    invalid_trip = {"id": "123"}  # Missing required fields
    is_valid = uber_processor._validate_trip_data(invalid_trip)
    assert is_valid is False


@pytest.mark.asyncio
async def test_calculate_trip_metrics(uber_processor, mock_api_response):
    """Test trip metrics calculation"""
    trip = mock_api_response["trips"][0]
    metrics = uber_processor._calculate_trip_metrics(trip)

    assert "duration" in metrics
    assert "avg_speed" in metrics
    assert "earnings_per_mile" in metrics


@pytest.mark.asyncio
async def test_format_trip_data(uber_processor, mock_api_response):
    """Test trip data formatting"""
    trip = mock_api_response["trips"][0]
    formatted_trip = uber_processor._format_trip_data(trip)

    assert formatted_trip["platform"] == "uber"
    assert formatted_trip["trip_id"] == trip["id"]
    assert formatted_trip["start_time"] == trip["start_time"]
    assert formatted_trip["end_time"] == trip["end_time"]


@pytest.mark.asyncio
async def test_error_handling(uber_processor):
    """Test error handling in trip processing"""
    with pytest.raises(ValueError):
        await uber_processor.process_trips(None)


@pytest.mark.asyncio
async def test_date_parsing(uber_processor, mock_api_response):
    """Test date parsing functionality"""
    trip = mock_api_response["trips"][0]
    parsed_date = uber_processor._parse_date(trip["start_time"])
    assert isinstance(parsed_date, datetime)


@pytest.mark.asyncio
async def test_distance_conversion(uber_processor):
    """Test distance conversion functionality"""
    miles = uber_processor._convert_to_miles(10.0)
    assert isinstance(miles, float)
    assert miles > 0
