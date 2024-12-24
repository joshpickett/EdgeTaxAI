import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
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
            'end_location': 'Downtown',
            'distance': 10.5,
            'date': '2023-01-01 09:00:00'
        },
        {
            'start_location': 'Downtown',
            'end_location': 'Home',
            'distance': 10.5,
            'date': '2023-01-01 17:00:00'
        }
    ]

def test_analyze_trip_patterns_success(trip_analyzer, mock_database, sample_trips):
    """Test successful trip pattern analysis"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_trips
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1)
    
    assert result['total_trips'] == 2
    assert result['total_miles'] == 21.0
    assert result['average_trip_length'] == 10.5
    assert len(result['common_routes']) > 0
    assert len(result['peak_hours']) == 24

def test_analyze_trip_patterns_no_data(trip_analyzer, mock_database):
    """Test trip pattern analysis with no data"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = []
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1)
    
    assert result['total_trips'] == 0
    assert result['total_miles'] == 0
    assert result['average_trip_length'] == 0
    assert len(result['common_routes']) == 0

def test_analyze_common_routes(trip_analyzer, sample_trips):
    """Test common routes analysis"""
    routes = trip_analyzer._analyze_common_routes(sample_trips)
    
    assert len(routes) > 0
    assert 'route' in routes[0]
    assert 'frequency' in routes[0]
    assert 'total_distance' in routes[0]
    assert 'average_distance' in routes[0]

def test_analyze_peak_hours(trip_analyzer, sample_trips):
    """Test peak hours analysis"""
    peak_hours = trip_analyzer._analyze_peak_hours(sample_trips)
    
    assert len(peak_hours) == 24
    assert '09' in peak_hours
    assert '17' in peak_hours

def test_get_earnings_per_mile_success(trip_analyzer, mock_database):
    """Test successful earnings per mile calculation"""
    mock_cursor = Mock()
    mock_cursor.fetchone.side_effect = [
        {'total_earnings': 1000.0},
        {'total_miles': 500.0}
    ]
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.get_earnings_per_mile(user_id=1)
    
    assert result['total_earnings'] == 1000.0
    assert result['total_miles'] == 500.0
    assert result['earnings_per_mile'] == 2.0

def test_get_earnings_per_mile_no_miles(trip_analyzer, mock_database):
    """Test earnings per mile with no miles driven"""
    mock_cursor = Mock()
    mock_cursor.fetchone.side_effect = [
        {'total_earnings': 1000.0},
        {'total_miles': 0}
    ]
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = trip_analyzer.get_earnings_per_mile(user_id=1)
    
    assert result['earnings_per_mile'] == 0

def test_analyze_trip_patterns_with_date_range(trip_analyzer, mock_database, sample_trips):
    """Test trip pattern analysis with date range"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_trips
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    date_range = (
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    
    result = trip_analyzer.analyze_trip_patterns(user_id=1, date_range=date_range)
    
    assert result['total_trips'] == 2
    assert 'peak_hours' in result
