import pytest
import os
from unittest.mock import Mock, patch
from ..utils.document_manager import (
    DocumentManager,
    DocumentError,
    DocumentValidationError,
)


class TestDocumentManager:
    @pytest.fixture
    def document_manager(self):
        return DocumentManager(database_path=":memory:")

    @pytest.fixture
    def mock_db(self):
        with patch("sqlite3.connect") as mock:
            yield mock

    def test_store_document_success(self, document_manager):
        data = {
            "user_id": 123,
            "type": "tax_return",
            "filename": "test.pdf",
            "content": {"data": "test content"},
            "metadata": {"year": 2023},
        }

        result = document_manager.store_document(data)

        assert "document_id" in result
        assert "filename" in result

    def test_validate_document_invalid_format(self, document_manager):
        file_data = {"filename": "test.xyz", "size": 1000}

        is_valid, message = document_manager.validate_document(file_data)
        assert not is_valid
        assert "Unsupported file format" in message

    def test_validate_document_size_limit(self, document_manager):
        file_data = {"filename": "test.pdf", "size": 20 * 1024 * 1024}  # 20MB

        is_valid, message = document_manager.validate_document(file_data)
        assert not is_valid
        assert "size exceeds maximum limit" in message

    def test_get_document_success(self, document_manager, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (
            1,
            123,
            "tax_return",
            "test.pdf",
            "{}",
            "2023-01-01",
        )

        document = document_manager.get_document(1)

        assert document is not None
        assert document["id"] == 1
        assert document["user_id"] == 123

    def test_get_user_documents(self, document_manager, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 123, "tax_return", "test1.pdf", "{}", "2023-01-01"),
            (2, 123, "receipt", "test2.pdf", "{}", "2023-01-02"),
        ]

        documents = document_manager.get_user_documents(123)

        assert len(documents) == 2
        assert all(doc["type"] in ["tax_return", "receipt"] for doc in documents)

    def test_delete_document_success(self, document_manager, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("test.pdf",)

        result = document_manager.delete_document(1)
        assert result is True

    def test_verify_document_success(self, document_manager):
        # First store a document
        data = {
            "user_id": 123,
            "type": "tax_return",
            "filename": "test.pdf",
            "content": {"data": "test content"},
            "metadata": {"tracking_id": "test123"},
        }
        stored_doc = document_manager.store_document(data)

        # Then verify it
        verification = document_manager.verify_document(stored_doc["document_id"])

        assert verification["status"] == "verified"
        assert "document" in verification

    def test_document_error_handling(self, document_manager):
        with pytest.raises(DocumentValidationError):
            document_manager.store_document({})

    def test_update_document_status(self, document_manager, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor

        document_manager._update_document_status(1, "verified")

        mock_cursor.execute.assert_called_once()
        mock_db.return_value.commit.assert_called_once()
