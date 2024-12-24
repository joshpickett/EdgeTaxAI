import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from api.utils.trip_analyzer import TripAnalyzer
from api.utils.db_utils import Database

@pytest.fixture
def mock_database():
    return Mock(spec=Database)

@pytest.fixture
def trip_analyzer(mock_database):
    return TripAnalyzer(mock_database)

@pytest.fixture
def sample_trips():
    return [
        {
            'start_location': 'Home',
            'end_location': 'Office',
            'distance': 10.5,
            'date': '2023-01-01 09:00:00'
        },
        {
            'start_location': 'Office',
            'end_location': 'Home',
            'distance': 10.5,
            'date': '2023-01-01 17:00:00'
        },
        {
            'start_location': 'Home',
            'end_location': 'Client A',
            'distance': 15.0,
            'date': '2023-01-02 10:00:00'
        }
    ]

def test_analyze_trip_patterns(trip_analyzer, mock_database, sample_trips):
    # Configure mock database to return sample trips
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_trips
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1)
    
    assert result['total_trips'] == 3
    assert result['total_miles'] == 36.0
    assert result['average_trip_length'] == 12.0
    assert len(result['common_routes']) <= 5
    assert isinstance(result['peak_hours'], dict)

def test_analyze_trip_patterns_empty(trip_analyzer, mock_database):
    # Test with no trips
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = []
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1)
    
    assert result['total_trips'] == 0
    assert result['total_miles'] == 0
    assert result['average_trip_length'] == 0
    assert len(result['common_routes']) == 0
    assert isinstance(result['peak_hours'], dict)

def test_analyze_common_routes(trip_analyzer, sample_trips):
    routes = trip_analyzer._analyze_common_routes(sample_trips)
    
    assert len(routes) > 0
    assert 'route' in routes[0]
    assert 'frequency' in routes[0]
    assert 'total_distance' in routes[0]
    assert 'average_distance' in routes[0]

def test_analyze_peak_hours(trip_analyzer, sample_trips):
    peak_hours = trip_analyzer._analyze_peak_hours(sample_trips)
    
    assert isinstance(peak_hours, dict)
    assert len(peak_hours) == 24  # Should have entry for each hour
    assert all(isinstance(count, int) for count in peak_hours.values())

def test_get_earnings_per_mile(trip_analyzer, mock_database):
    # Mock earnings and mileage data
    mock_cursor = Mock()
    mock_cursor.fetchone.side_effect = [
        {'total_earnings': 1000},
        {'total_miles': 100}
    ]
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.get_earnings_per_mile(user_id=1)
    
    assert result['total_earnings'] == 1000
    assert result['total_miles'] == 100
    assert result['earnings_per_mile'] == 10.0

def test_get_cached_analysis(trip_analyzer):
    # Test cache functionality
    user_id = 1
    date_range = ('2023-01-01', '2023-01-31')
    
    # First call should return None
    result = trip_analyzer.get_cached_analysis(user_id, date_range)
    assert result is None
    
    # Add data to cache
    cached_data = {'total_trips': 5, 'total_miles': 50}
    trip_analyzer.cache[f"{user_id}_{date_range}"] = {
        'data': cached_data,
        'timestamp': datetime.now()
    }
    
    # Second call should return cached data
    result = trip_analyzer.get_cached_analysis(user_id, date_range)
    assert result == cached_data

def test_error_handling(trip_analyzer, mock_database):
    # Test error handling when database fails
    mock_database.get_cursor.side_effect = Exception("Database error")
    
    with pytest.raises(Exception):
        trip_analyzer.analyze_trip_patterns(user_id=1)
