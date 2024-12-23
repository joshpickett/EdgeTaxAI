import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from api.utils.analytics_integration import AnalyticsIntegration
from api.utils.db_utils import Database

@pytest.fixture
def mock_db():
    return Mock(spec=Database)

@pytest.fixture
def analytics_integration(mock_db):
    return AnalyticsIntegration(mock_db)

@pytest.fixture
def sample_analytics_data():
    return {
        'total_earnings': 1000.0,
        'expenses': 200.0,
        'net_income': 800.0,
        'platform_breakdown': [
            {'platform': 'uber', 'amount': 600.0},
            {'platform': 'lyft', 'amount': 400.0}
        ]
    }

def test_get_user_analytics_cache_hit(analytics_integration):
    """Test analytics retrieval when data is in cache"""
    with patch('api.utils.analytics_integration.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = {'cached': 'data'}
        
        result = analytics_integration.get_user_analytics(user_id=1)
        
        assert result == {'cached': 'data'}
        mock_cache.return_value.get.assert_called_once()

def test_get_user_analytics_cache_miss(analytics_integration, sample_analytics_data):
    """Test analytics retrieval when data is not in cache"""
    with patch('api.utils.analytics_integration.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = None
        mock_cache.return_value.set.return_value = True
        
        with patch.object(analytics_integration.analytics, 
                         'get_comprehensive_report', 
                         return_value=sample_analytics_data):
            result = analytics_integration.get_user_analytics(user_id=1)
            
            assert result == sample_analytics_data
            mock_cache.return_value.set.assert_called_once()

def test_refresh_analytics(analytics_integration, sample_analytics_data):
    """Test analytics refresh functionality"""
    with patch('api.utils.analytics_integration.CacheManager') as mock_cache:
        with patch.object(analytics_integration.analytics, 
                         'get_comprehensive_report', 
                         return_value=sample_analytics_data):
            analytics_integration.refresh_analytics(user_id=1)
            
            # Verify cache clearing and setting
            mock_cache.return_value.delete.assert_called()
            mock_cache.return_value.set.assert_called()

def test_get_platform_comparison(analytics_integration):
    """Test platform comparison functionality"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = {
        'total_earnings': 1000.0,
        'trip_count': 50,
        'avg_earnings': 20.0
    }
    
    analytics_integration.db.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = analytics_integration.get_platform_comparison(
        user_id=1, 
        platforms=['uber', 'lyft']
    )
    
    assert 'platform_metrics' in result
    assert 'top_platform' in result
    assert 'comparison_period' in result

def test_get_earnings_trends_daily(analytics_integration):
    """Test daily earnings trends analysis"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {'period': '2023-01-01', 'total_earnings': 100.0, 'transaction_count': 5},
        {'period': '2023-01-02', 'total_earnings': 150.0, 'transaction_count': 7}
    ]
    
    analytics_integration.db.get_cursor.return_value.__enter__.return_value = mock_cursor
    
    result = analytics_integration.get_earnings_trends(user_id=1, period='daily')
    
    assert result['period_type'] == 'daily'
    assert len(result['trends']) == 2
    assert 'average_per_period' in result

def test_error_handling(analytics_integration):
    """Test error handling in analytics integration"""
    with patch.object(analytics_integration.db, 'get_cursor') as mock_cursor:
        mock_cursor.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            analytics_integration.get_platform_comparison(user_id=1, platforms=['uber'])
        
        assert "Database error" in str(exc_info.value)

def test_cache_timeout(analytics_integration, sample_analytics_data):
    """Test cache timeout functionality"""
    with patch('api.utils.analytics_integration.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = None
        
        with patch.object(analytics_integration.analytics, 
                         'get_comprehensive_report', 
                         return_value=sample_analytics_data):
            analytics_integration.get_user_analytics(user_id=1)
            
            mock_cache.return_value.set.assert_called_once_with(
                mock_cache.return_value.set.call_args[0][0],
                sample_analytics_data,
                timeout=3600
            )

def test_period_filtering(analytics_integration):
    """Test analytics with period filtering"""
    period = (datetime.now() - timedelta(days=30), datetime.now())
    
    with patch('api.utils.analytics_integration.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = None
        
        result = analytics_integration.get_user_analytics(user_id=1, period=period)
        
        assert isinstance(result, dict)
        mock_cache.return_value.get.assert_called_once()
