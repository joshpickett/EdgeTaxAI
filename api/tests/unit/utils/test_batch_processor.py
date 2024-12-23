import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from api.utils.batch_processor import BatchProcessor

@pytest.fixture
def batch_processor():
    return BatchProcessor()

@pytest.fixture
def sample_files():
    return [
        {
            'filename': 'test1.pdf',
            'content': b'test content 1',
            'metadata': {'type': 'receipt'}
        },
        {
            'filename': 'test2.pdf',
            'content': b'test content 2',
            'metadata': {'type': 'invoice'}
        }
    ]

@pytest.mark.asyncio
async def test_process_batch_success(batch_processor, sample_files):
    """Test successful batch processing"""
    with patch.object(batch_processor, 'process_single_file', 
                     new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {'status': 'success'}
        
        batch_id = await batch_processor.process_batch(sample_files, user_id='123')
        
        assert batch_id.startswith('batch_123_')
        assert batch_processor.status_cache[batch_id]['total'] == 2
        assert batch_processor.status_cache[batch_id]['status'] == 'completed'

@pytest.mark.asyncio
async def test_process_batch_failure(batch_processor, sample_files):
    """Test batch processing with failures"""
    with patch.object(batch_processor, 'process_single_file', 
                     side_effect=Exception('Processing error')):
        batch_id = await batch_processor.process_batch(sample_files, user_id='123')
        
        assert batch_processor.status_cache[batch_id]['status'] == 'failed'
        assert 'error' in batch_processor.status_cache[batch_id]

@pytest.mark.asyncio
async def test_process_single_file_success(batch_processor):
    """Test successful single file processing"""
    file_data = {
        'filename': 'test.pdf',
        'content': b'test content',
        'metadata': {'type': 'receipt'}
    }
    
    with patch.object(batch_processor, 'extract_receipt_data', 
                     new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = {'total': 100.0, 'date': '2023-01-01'}
        
        result = await batch_processor.process_single_file(
            file_data, 
            batch_id='test_batch'
        )
        
        assert result['status'] == 'success'
        assert 'confidence_score' in result
        assert 'processing_time' in result

def test_get_batch_status_cache_hit(batch_processor):
    """Test batch status retrieval from cache"""
    with patch('api.utils.batch_processor.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = {'status': 'completed'}
        
        status = batch_processor.get_batch_status('test_batch')
        
        assert status['status'] == 'completed'
        mock_cache.return_value.get.assert_called_once()

def test_get_batch_status_cache_miss(batch_processor):
    """Test batch status retrieval from status cache"""
    with patch('api.utils.batch_processor.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = None
        batch_processor.status_cache['test_batch'] = {'status': 'processing'}
        
        status = batch_processor.get_batch_status('test_batch')
        
        assert status['status'] == 'processing'

def test_get_batch_status_not_found(batch_processor):
    """Test batch status retrieval for non-existent batch"""
    with patch('api.utils.batch_processor.CacheManager') as mock_cache:
        mock_cache.return_value.get.return_value = None
        
        status = batch_processor.get_batch_status('nonexistent_batch')
        
        assert status['status'] == 'not_found'
        assert status['processed'] == 0

def test_calculate_confidence_score(batch_processor):
    """Test confidence score calculation"""
    result = {
        'total': 100.0,
        'date': '2023-01-01',
        'vendor': 'Test Vendor'
    }
    
    score = batch_processor.calculate_confidence_score(result)
    assert score == 1.0  # All required fields present
    
    result = {
        'total': 100.0,
        'date': '2023-01-01'
    }
    
    score = batch_processor.calculate_confidence_score(result)
    assert score == 2/3  # Two out of three required fields present

@pytest.mark.asyncio
async def test_batch_processing_with_empty_files(batch_processor):
    """Test batch processing with empty file list"""
    batch_id = await batch_processor.process_batch([], user_id='123')
    
    assert batch_processor.status_cache[batch_id]['total'] == 0
    assert batch_processor.status_cache[batch_id]['status'] == 'completed'

def test_batch_status_caching(batch_processor):
    """Test batch status caching mechanism"""
    with patch('api.utils.batch_processor.CacheManager') as mock_cache:
        batch_processor.status_cache['test_batch'] = {
            'status': 'completed',
            'results': ['result1', 'result2']
        }
        
        batch_processor.get_batch_status('test_batch')
        
        mock_cache.return_value.set.assert_called_once()
