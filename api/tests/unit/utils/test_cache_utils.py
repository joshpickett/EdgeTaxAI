import pytest
from unittest.mock import Mock, patch
from api.utils.cache_utils import CacheManager, cache_response


@pytest.fixture
def cache_manager():
    return CacheManager()


@pytest.fixture
def mock_redis():
    with patch("api.utils.cache_utils.redis_client") as mock_redis:
        yield mock_redis


def test_get_success(cache_manager, mock_redis):
    """Test successful cache retrieval"""
    mock_redis.get.return_value = '{"key": "value"}'
    result = cache_manager.get("test_key")

    assert result == {"key": "value"}
    mock_redis.get.assert_called_once_with("test_key")


def test_get_none(cache_manager, mock_redis):
    """Test cache retrieval with no data"""
    mock_redis.get.return_value = None
    result = cache_manager.get("test_key")

    assert result is None
    mock_redis.get.assert_called_once_with("test_key")


def test_get_error(cache_manager, mock_redis):
    """Test cache retrieval error handling"""
    mock_redis.get.side_effect = Exception("Redis error")
    result = cache_manager.get("test_key")

    assert result is None


def test_set_success(cache_manager, mock_redis):
    """Test successful cache setting"""
    mock_redis.setex.return_value = True
    result = cache_manager.set("test_key", {"data": "test"}, 3600)

    assert result is True
    mock_redis.setex.assert_called_once()


def test_set_error(cache_manager, mock_redis):
    """Test cache setting error handling"""
    mock_redis.setex.side_effect = Exception("Redis error")
    result = cache_manager.set("test_key", {"data": "test"})

    assert result is False


def test_delete_success(cache_manager, mock_redis):
    """Test successful cache deletion"""
    mock_redis.delete.return_value = 1
    result = cache_manager.delete("test_key")

    assert result is True
    mock_redis.delete.assert_called_once_with("test_key")


def test_delete_not_found(cache_manager, mock_redis):
    """Test cache deletion when key not found"""
    mock_redis.delete.return_value = 0
    result = cache_manager.delete("test_key")

    assert result is False


def test_get_platform_data_success(cache_manager, mock_redis):
    """Test successful platform data retrieval"""
    mock_redis.get.return_value = '{"earnings": 100}'
    result = cache_manager.get_platform_data(1, "uber")

    assert result == {"earnings": 100}
    mock_redis.get.assert_called_once_with("platform_data:1:uber")


def test_set_platform_data_success(cache_manager, mock_redis):
    """Test successful platform data setting"""
    data = {"earnings": 100}
    result = cache_manager.set_platform_data(1, "uber", data)

    assert result is True
    mock_redis.setex.assert_called_once()


@patch("api.utils.cache_utils.CacheManager")
def test_cache_response_decorator(mock_cache_manager):
    """Test cache_response decorator"""
    mock_instance = Mock()
    mock_cache_manager.return_value = mock_instance
    mock_instance.get.return_value = None

    @cache_response(timeout=3600)
    def test_function():
        return {"data": "test"}

    result = test_function()

    assert result == {"data": "test"}
    mock_instance.set.assert_called_once()


@patch("api.utils.cache_utils.CacheManager")
def test_cache_response_hit(mock_cache_manager):
    """Test cache_response decorator with cache hit"""
    mock_instance = Mock()
    mock_cache_manager.return_value = mock_instance
    mock_instance.get.return_value = {"cached": "data"}

    @cache_response(timeout=3600)
    def test_function():
        return {"data": "test"}

    result = test_function()

    assert result == {"cached": "data"}
    mock_instance.set.assert_not_called()


def test_invalidate_platform_cache_success(cache_manager, mock_redis):
    """Test successful platform cache invalidation"""
    mock_redis.delete.return_value = 1
    result = cache_manager.invalidate_platform_cache(1, "uber")

    assert result is True
    mock_redis.delete.assert_called_once_with("platform_data:1:uber")


def test_cache_manager_default_timeout(cache_manager):
    """Test cache manager default timeout"""
    assert cache_manager.default_timeout == 3600
