import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from api.utils.gig_platform_processor import GigPlatformProcessor

@pytest.fixture
def gig_processor():
    return GigPlatformProcessor()

@pytest.fixture
def mock_uber_data():
    return {
        'trips': [
            {
                'id': 'uber123',
                'start_time': '2023-01-01T10:00:00Z',
                'end_time': '2023-01-01T10:30:00Z',
                'distance': 10.5,
                'earnings': 25.50,
                'status': 'completed'
            }
        ]
    }

@pytest.mark.asyncio
async def test_process_platform_data_success(gig_processor, mock_uber_data):
    """Test successful platform data processing"""
    with patch('api.utils.gig_platform_processor.UberProcessor') as mock_uber:
        mock_uber.return_value.process_trips.return_value = [
            {'trip_id': 'uber123', 'earnings': 25.50}
        ]
        mock_uber.return_value.process_earnings.return_value = {
            'total_earnings': 25.50
        }
        
        result = await gig_processor.process_platform_data('uber', mock_uber_data)
        
        assert result['platform'] == 'uber'
        assert 'trips' in result
        assert 'earnings' in result
        assert 'processed_at' in result

@pytest.mark.asyncio
async def test_process_platform_data_invalid_platform(gig_processor):
    """Test processing with invalid platform"""
    with pytest.raises(ValueError):
        await gig_processor.process_platform_data('invalid_platform', {})

@pytest.mark.asyncio
async def test_auto_sync_platforms(gig_processor):
    """Test auto-sync functionality"""
    with patch.object(gig_processor, '_perform_sync') as mock_sync:
        mock_sync.return_value = True
        await gig_processor.auto_sync_platforms()
        mock_sync.assert_called()

@pytest.mark.asyncio
async def test_retry_failed_sync(gig_processor):
    """Test retry mechanism for failed syncs"""
    with patch.object(gig_processor, '_perform_sync') as mock_sync:
        mock_sync.side_effect = [False, False, True]
        result = await gig_processor.retry_failed_sync(1, 'uber')
        assert result is True
        assert mock_sync.call_count == 3

def test_should_sync(gig_processor):
    """Test sync timing logic"""
    # Test with old sync time
    old_sync = (datetime.now() - timedelta(days=2)).isoformat()
    assert gig_processor._should_sync(old_sync) is True
    
    # Test with recent sync
    recent_sync = datetime.now().isoformat()
    assert gig_processor._should_sync(recent_sync) is False

@pytest.mark.asyncio
async def test_process_with_retry(gig_processor):
    """Test retry logic for processing"""
    mock_func = AsyncMock(side_effect=[Exception(), Exception(), "success"])
    result = await gig_processor._process_with_retry(mock_func, {})
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_create_expense_entries(gig_processor):
    """Test expense entry creation"""
    trips = [
        {
            'id': 'trip123',
            'description': 'Test trip',
            'expenses': 50.0,
            'type': 'rides'
        }
    ]
    
    with patch.object(gig_processor.conn, 'cursor') as mock_cursor:
        await gig_processor._create_expense_entries(trips, 'uber')
        mock_cursor.return_value.execute.assert_called_once()

@pytest.mark.asyncio
async def test_store_income_data(gig_processor):
    """Test income data storage"""
    earnings = {
        'user_id': 1,
        'gross_earnings': 100.0,
        'period_start': '2023-01-01',
        'period_end': '2023-01-31'
    }
    
    with patch.object(gig_processor.conn, 'cursor') as mock_cursor:
        await gig_processor._store_income_data(earnings, 'uber')
        mock_cursor.return_value.execute.assert_called_once()

def test_validate_processed_data(gig_processor):
    """Test data validation"""
    valid_data = {
        'trips': [{'id': 1}],
        'earnings': {'gross_earnings': 100, 'net_earnings': 80}
    }
    
    # Should not raise exception
    gig_processor._validate_processed_data(
        valid_data['trips'],
        valid_data['earnings']
    )
    
    # Test invalid data
    with pytest.raises(ValueError):
        gig_processor._validate_processed_data(
            "invalid",
            valid_data['earnings']
        )

@pytest.mark.asyncio
async def test_sync_worker(gig_processor):
    """Test background sync worker"""
    mock_task = {'user_id': 1, 'platform': 'uber'}
    
    with patch.object(gig_processor, '_process_sync_task') as mock_process:
        await gig_processor.start_sync_worker()
        await gig_processor.sync_queue.put(mock_task)
        await gig_processor.stop_sync_worker()
        
        mock_process.assert_called_once_with(mock_task)
