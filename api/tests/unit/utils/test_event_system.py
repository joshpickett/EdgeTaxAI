import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.event_system import EventSystem


@pytest.fixture
def event_system():
    return EventSystem()


def test_subscribe_event(event_system):
    """Test event subscription"""
    callback = Mock()
    event_system.subscribe("test_event", callback)

    assert "test_event" in event_system._subscribers
    assert callback in event_system._subscribers["test_event"]


def test_publish_event(event_system):
    """Test event publishing"""
    callback = Mock()
    event_system.subscribe("test_event", callback)

    test_data = {"message": "test"}
    event_system.publish("test_event", test_data)

    callback.assert_called_once_with(test_data)


def test_publish_event_multiple_subscribers(event_system):
    """Test event publishing to multiple subscribers"""
    callback1 = Mock()
    callback2 = Mock()
    event_system.subscribe("test_event", callback1)
    event_system.subscribe("test_event", callback2)

    test_data = {"message": "test"}
    event_system.publish("test_event", test_data)

    callback1.assert_called_once_with(test_data)
    callback2.assert_called_once_with(test_data)


def test_publish_event_no_subscribers(event_system):
    """Test publishing event with no subscribers"""
    test_data = {"message": "test"}
    event_system.publish("test_event", test_data)

    # Should not raise any exception
    assert len(event_system.get_history()) == 1


def test_callback_error_handling(event_system):
    """Test error handling in event callbacks"""

    def failing_callback(data):
        raise Exception("Callback error")

    event_system.subscribe("test_event", failing_callback)
    test_data = {"message": "test"}

    # Should not raise exception
    event_system.publish("test_event", test_data)


def test_event_history(event_system):
    """Test event history tracking"""
    test_data = {"message": "test"}
    event_system.publish("test_event", test_data)

    history = event_system.get_history()
    assert len(history) == 1
    assert history[0]["type"] == "test_event"
    assert history[0]["data"] == test_data
    assert "timestamp" in history[0]


def test_multiple_event_types(event_system):
    """Test handling multiple event types"""
    callback1 = Mock()
    callback2 = Mock()
    event_system.subscribe("event1", callback1)
    event_system.subscribe("event2", callback2)

    event_system.publish("event1", {"message": "test1"})
    event_system.publish("event2", {"message": "test2"})

    callback1.assert_called_once_with({"message": "test1"})
    callback2.assert_called_once_with({"message": "test2"})


def test_event_timestamp(event_system):
    """Test event timestamp format"""
    event_system.publish("test_event", {"message": "test"})

    history = event_system.get_history()
    timestamp = datetime.fromisoformat(history[0]["timestamp"])
    assert isinstance(timestamp, datetime)


def test_subscribe_multiple_times(event_system):
    """Test subscribing same callback multiple times"""
    callback = Mock()
    event_system.subscribe("test_event", callback)
    event_system.subscribe("test_event", callback)

    test_data = {"message": "test"}
    event_system.publish("test_event", test_data)

    assert callback.call_count == 2


def test_publish_with_empty_data(event_system):
    """Test publishing event with empty data"""
    callback = Mock()
    event_system.subscribe("test_event", callback)

    event_system.publish("test_event", {})

    callback.assert_called_once_with({})
