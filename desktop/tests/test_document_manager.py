import pytest
from unittest.mock import Mock, patch
from desktop.document_manager import DocumentManager
import os


@pytest.fixture
def doc_manager():
    return DocumentManager(api_base_url="http://test-api")


@pytest.fixture
def mock_requests():
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        yield {"post": mock_post, "get": mock_get}


def test_process_document_upload_success(doc_manager, mock_requests):
    # Arrange
    mock_file = Mock()
    mock_file.name = "test.pdf"
    mock_file.size = 1024 * 1024  # 1MB

    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests["post"].return_value = mock_response

    # Act
    result = doc_manager.process_document_upload(
        file=mock_file, document_type="tax_return", user_id=123
    )

    # Assert
    assert result is True
    mock_requests["post"].assert_called_once()


def test_process_document_upload_invalid_format(doc_manager):
    # Arrange
    mock_file = Mock()
    mock_file.name = "test.txt"
    mock_file.size = 1024 * 1024

    # Act
    result = doc_manager.process_document_upload(
        file=mock_file, document_type="tax_return", user_id=123
    )

    # Assert
    assert result is False


def test_process_document_upload_file_too_large(doc_manager):
    # Arrange
    mock_file = Mock()
    mock_file.name = "test.pdf"
    mock_file.size = 11 * 1024 * 1024  # 11MB

    # Act
    result = doc_manager.process_document_upload(
        file=mock_file, document_type="tax_return", user_id=123
    )

    # Assert
    assert result is False


def test_get_documents_success(doc_manager, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"documents": [{"id": 1}]}
    mock_requests["get"].return_value = mock_response

    # Act
    result = doc_manager.get_documents(user_id=123)

    # Assert
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_download_document_success(doc_manager, mock_requests):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"test content"
    mock_requests["get"].return_value = mock_response

    # Act
    result = doc_manager.download_document("doc123")

    # Assert
    assert result == b"test content"
