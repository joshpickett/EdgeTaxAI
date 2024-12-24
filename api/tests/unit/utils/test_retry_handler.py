import pytest
from unittest.mock import Mock, patch
import asyncio
from api.utils.retry_handler import RetryHandler, with_retry

@pytest.fixture
def retry_handler():
    return RetryHandler(max_attempts=3, initial_delay=0.1)

@pytest.mark.asyncio
async def test_retry_success_first_attempt(retry_handler):
    """Test successful execution on first attempt"""
    mock_function = Mock()
    mock_function.return_value = "success"
    
    result = await retry_handler.retry_with_backoff(mock_function)
    
    assert result == "success"
    assert mock_function.call_count == 1

@pytest.mark.asyncio
async def test_retry_success_after_failures(retry_handler):
    """Test successful execution after failures"""
    mock_function = Mock(side_effect=[Exception("Error"), Exception("Error"), "success"])
    
    result = await retry_handler.retry_with_backoff(mock_function)
    
    assert result == "success"
    assert mock_function.call_count == 3

@pytest.mark.asyncio
async def test_retry_all_attempts_failed(retry_handler):
    """Test when all retry attempts fail"""
    mock_function = Mock(side_effect=Exception("Persistent error"))
    
    with pytest.raises(Exception) as exception_info:
        await retry_handler.retry_with_backoff(mock_function)
    
    assert str(exception_info.value) == "Persistent error"
    assert mock_function.call_count == 3

@pytest.mark.asyncio
async def test_retry_with_args(retry_handler):
    """Test retry with function arguments"""
    mock_function = Mock()
    await retry_handler.retry_with_backoff(mock_function, 1, key="value")
    
    mock_function.assert_called_with(1, key="value")

@pytest.mark.asyncio
async def test_retry_decorator():
    """Test retry decorator functionality"""
    attempts = 0
    
    @with_retry(max_attempts=3, initial_delay=0.1)
    async def test_function():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise Exception("Test error")
        return "success"
    
    result = await test_function()
    
    assert result == "success"
    assert attempts == 2

@pytest.mark.asyncio
async def test_retry_exponential_backoff(retry_handler):
    """Test exponential backoff timing"""
    mock_function = Mock(side_effect=[Exception("Error"), Exception("Error"), "success"])
    start_time = asyncio.get_event_loop().time()
    
    await retry_handler.retry_with_backoff(mock_function)
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    assert elapsed_time >= 0.3  # 0.1 + 0.2 seconds minimum

@pytest.mark.asyncio
async def test_retry_custom_exception(retry_handler):
    """Test retry with specific exception type"""
    class CustomError(Exception):
        pass
    
    mock_function = Mock(side_effect=[CustomError("Custom"), "success"])
    
    result = await retry_handler.retry_with_backoff(mock_function)
    
    assert result == "success"
    assert mock_function.call_count == 2

@pytest.mark.asyncio
async def test_retry_immediate_success(retry_handler):
    """Test immediate success without retries"""
    mock_function = Mock(return_value="immediate success")
    
    result = await retry_handler.retry_with_backoff(mock_function)
    
    assert result == "immediate success"
    assert mock_function.call_count == 1
