import pytest
from datetime import datetime
from api.utils.response_formatter import ResponseFormatter


@pytest.fixture
def response_formatter():
    return ResponseFormatter()


def test_format_response_success():
    """Test successful response formatting"""
    data = {"key": "value"}
    response = ResponseFormatter.format_response(data)

    assert response["status"] == "success"
    assert "timestamp" in response
    assert response["data"] == data
    assert isinstance(datetime.fromisoformat(response["timestamp"]), datetime)


def test_format_response_with_message():
    """Test response formatting with message"""
    data = {"key": "value"}
    message = "Test message"
    response = ResponseFormatter.format_response(data, message=message)

    assert response["message"] == message
    assert response["data"] == data


def test_format_response_with_metadata():
    """Test response formatting with metadata"""
    data = {"key": "value"}
    metadata = {"meta_key": "meta_value"}
    response = ResponseFormatter.format_response(data, metadata=metadata)

    assert response["metadata"] == metadata
    assert response["data"] == data


def test_format_error_basic():
    """Test basic error formatting"""
    message = "Test error"
    response = ResponseFormatter.format_error(message)

    assert response["status"] == "error"
    assert response["error"]["message"] == message
    assert "timestamp" in response


def test_format_error_with_code():
    """Test error formatting with error code"""
    message = "Test error"
    error_code = "ERR001"
    response = ResponseFormatter.format_error(message, error_code=error_code)

    assert response["error"]["code"] == error_code
    assert response["error"]["message"] == message


def test_format_error_with_details():
    """Test error formatting with details"""
    message = "Test error"
    details = {"field": "username", "issue": "required"}
    response = ResponseFormatter.format_error(message, details=details)

    assert response["error"]["details"] == details
    assert response["error"]["message"] == message


def test_format_batch_response_success():
    """Test successful batch response formatting"""
    batch_id = "batch123"
    total = 10
    processed = 10
    failed = 0
    results = [{"id": 1, "status": "success"}]

    response = ResponseFormatter.format_batch_response(
        batch_id, total, processed, failed, results
    )

    assert response["status"] == "success"
    assert response["batch_id"] == batch_id
    assert response["summary"]["success_rate"] == 1.0
    assert response["results"] == results


def test_format_batch_response_partial_success():
    """Test batch response formatting with partial success"""
    batch_id = "batch123"
    total = 10
    processed = 8
    failed = 2
    results = [{"id": 1, "status": "success"}, {"id": 2, "status": "failed"}]

    response = ResponseFormatter.format_batch_response(
        batch_id, total, processed, failed, results
    )

    assert response["status"] == "partial_success"
    assert response["summary"]["success_rate"] == 0.6
    assert len(response["results"]) == 2


def test_format_batch_response_with_metadata():
    """Test batch response formatting with metadata"""
    batch_id = "batch123"
    metadata = {"processor": "test_processor"}

    response = ResponseFormatter.format_batch_response(
        batch_id, 1, 1, 0, [], metadata=metadata
    )

    assert response["metadata"] == metadata


def test_format_batch_response_zero_total():
    """Test batch response formatting with zero total"""
    response = ResponseFormatter.format_batch_response("batch123", 0, 0, 0, [])

    assert response["summary"]["success_rate"] == 0
