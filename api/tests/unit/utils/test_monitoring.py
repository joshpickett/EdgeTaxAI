import pytest
from unittest.mock import Mock, patch
from api.utils.monitoring import monitor_api_calls, get_api_metrics, clear_metrics
import time


@pytest.fixture
def mock_redis():
    with patch("api.utils.monitoring.redis_client") as mock:
        yield mock


def test_monitor_api_calls_success(mock_redis):
    """Test successful Application Programming Interface call monitoring"""

    @monitor_api_calls("test_endpoint")
    async def test_function():
        return "success"

    result = await test_function()

    assert result == "success"
    mock_redis.incr.assert_called_with("api_calls:test_endpoint")
    mock_redis.expire.assert_called()


def test_monitor_api_calls_error(mock_redis):
    """Test Application Programming Interface call monitoring with error"""

    @monitor_api_calls("test_endpoint")
    async def test_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await test_function()

    mock_redis.incr.assert_called_with("errors:test_endpoint")


def test_get_api_metrics_success(mock_redis):
    """Test successful metrics retrieval"""
    mock_redis.get.side_effect = [b"100", b"5"]  # calls and errors
    mock_redis.lrange.return_value = [b"0.5", b"0.3", b"0.4"]  # response times

    metrics = get_api_metrics("test_endpoint")

    assert metrics["total_calls"] == 100
    assert metrics["error_count"] == 5
    assert metrics["error_rate"] == 5.0
    assert metrics["avg_response_time"] == 0.4


def test_get_api_metrics_no_data(mock_redis):
    """Test metrics retrieval with no data"""
    mock_redis.get.return_value = None
    mock_redis.lrange.return_value = []

    metrics = get_api_metrics("test_endpoint")

    assert metrics["total_calls"] == 0
    assert metrics["error_count"] == 0
    assert metrics["error_rate"] == 0
    assert metrics["avg_response_time"] == 0


def test_clear_metrics_specific_endpoint(mock_redis):
    """Test clearing metrics for specific endpoint"""
    clear_metrics("test_endpoint")

    mock_redis.delete.assert_any_call("api_calls:test_endpoint")
    mock_redis.delete.assert_any_call("errors:test_endpoint")
    mock_redis.delete.assert_any_call("response_times:test_endpoint")


def test_clear_metrics_all_endpoints(mock_redis):
    """Test clearing metrics for all endpoints"""
    mock_redis.keys.return_value = ["api_calls:test1", "api_calls:test2"]

    clear_metrics()

    assert mock_redis.delete.call_count >= 2


def test_rate_limiting(mock_redis):
    """Test rate limiting functionality"""
    mock_redis.get.return_value = b"101"  # Over rate limit

    @monitor_api_calls("test_endpoint")
    async def test_function():
        return "success"

    with pytest.raises(Exception) as exc_info:
        await test_function()

    assert "Rate limit exceeded" in str(exc_info.value)


def test_response_time_tracking(mock_redis):
    """Test response time tracking"""

    @monitor_api_calls("test_endpoint")
    async def test_function():
        time.sleep(0.1)
        return "success"

    result = await test_function()

    assert result == "success"
    assert mock_redis.lpush.called


def test_error_tracking_with_type(mock_redis):
    """Test error tracking with specific error type"""

    @monitor_api_calls("test_endpoint")
    async def test_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await test_function()

    mock_redis.incr.assert_called_with("errors:test_endpoint")


def test_metrics_expiration(mock_redis):
    """Test metrics expiration setting"""

    @monitor_api_calls("test_endpoint")
    async def test_function():
        return "success"

    await test_function()

    mock_redis.expire.assert_called_with("api_calls:test_endpoint", 86400)
