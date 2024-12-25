import pytest
from datetime import datetime, timedelta
from api.utils.trip_analyzer import TripAnalyzer
from api.utils.db_utils import Database

@pytest.fixture
def mock_database(mocker):
    mock_database_instance = mocker.Mock(spec=Database)
    mock_cursor = mocker.Mock()
    mock_database_instance.get_cursor.return_value.__enter__.return_value = mock_cursor
    return mock_database_instance

@pytest.fixture
def trip_analyzer(mock_database):
    return TripAnalyzer(mock_database)

def test_analyze_trip_patterns_empty(trip_analyzer, mock_database):
    mock_database.get_cursor().fetchall.return_value = []
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1)
    assert result['total_trips'] == 0
    assert result['total_miles'] == 0
    assert result['average_trip_length'] == 0
    assert result['common_routes'] == []

def test_analyze_trip_patterns_success(trip_analyzer, mock_database):
    mock_trips = [
        {'start_location': 'A', 'end_location': 'B', 'distance': 10.0, 'date': '2023-01-01 10:00:00'},
        {'start_location': 'A', 'end_location': 'B', 'distance': 10.0, 'date': '2023-01-02 11:00:00'},
        {'start_location': 'B', 'end_location': 'C', 'distance': 15.0, 'date': '2023-01-03 12:00:00'}
    ]
    mock_database.get_cursor().fetchall.return_value = mock_trips
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1)
    assert result['total_trips'] == 3
    assert result['total_miles'] == 35.0
    assert result['average_trip_length'] == pytest.approx(11.67, 0.01)
    assert len(result['common_routes']) > 0

def test_analyze_common_routes(trip_analyzer):
    trips = [
        {'start_location': 'A', 'end_location': 'B', 'distance': 10.0, 'date': '2023-01-01'},
        {'start_location': 'A', 'end_location': 'B', 'distance': 10.0, 'date': '2023-01-02'},
        {'start_location': 'B', 'end_location': 'C', 'distance': 15.0, 'date': '2023-01-03'}
    ]
    
    routes = trip_analyzer._analyze_common_routes(trips)
    assert len(routes) == 2
    assert routes[0]['frequency'] == 2  # A to B is most common
    assert routes[0]['total_distance'] == 20.0
    assert routes[0]['average_distance'] == 10.0

def test_analyze_peak_hours(trip_analyzer):
    trips = [
        {'date': '2023-01-01 09:00:00'},
        {'date': '2023-01-01 09:30:00'},
        {'date': '2023-01-01 14:00:00'}
    ]
    
    peak_hours = trip_analyzer._analyze_peak_hours(trips)
    assert peak_hours['09'] == 2  # Most trips at 9AM
    assert peak_hours['14'] == 1

def test_get_earnings_per_mile_success(trip_analyzer, mock_database):
    mock_database.get_cursor().fetchone.side_effect = [
        {'total_earnings': 100.0},
        {'total_miles': 50.0}
    ]
    
    result = trip_analyzer.get_earnings_per_mile(user_id=1)
    assert result['total_earnings'] == 100.0
    assert result['total_miles'] == 50.0
    assert result['earnings_per_mile'] == 2.0

def test_get_earnings_per_mile_no_data(trip_analyzer, mock_database):
    mock_database.get_cursor().fetchone.side_effect = [
        {'total_earnings': 0},
        {'total_miles': 0}
    ]
    
    result = trip_analyzer.get_earnings_per_mile(user_id=1)
    assert result['total_earnings'] == 0
    assert result['total_miles'] == 0
    assert result['earnings_per_mile'] == 0

def test_get_cached_analysis(trip_analyzer):
    user_id = 1
    date_range = ('2023-01-01', '2023-01-31')
    
    # Test with no cache
    result = trip_analyzer.get_cached_analysis(user_id, date_range)
    assert result is None
    
    # Test with expired cache
    trip_analyzer.cache[f"{user_id}_{date_range}"] = {
        'timestamp': datetime.now() - timedelta(hours=2),
        'data': {'test': 'data'}
    }
    result = trip_analyzer.get_cached_analysis(user_id, date_range)
    assert result is None
