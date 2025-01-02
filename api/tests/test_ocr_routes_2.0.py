import pytest
from unittest.mock import Mock, patch, mock_open
from ..routes.ocr_routes import ocr_bp
import json
import os


@pytest.fixture
def app():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(ocr_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_vision_client():
    with patch("google.cloud.vision.ImageAnnotatorClient") as mock:
        yield mock


class TestOCRRoutes:
    def test_process_receipt_success(self, client, mock_vision_client):
        # Mock file upload
        mock_file = (open("tests/test_data/sample_receipt.jpg", "rb"), "receipt.jpg")

        # Mock Vision Application Programming Interface response
        mock_response = Mock()
        mock_response.text_annotations = [
            Mock(description="Test Receipt\nAmount: $50.00")
        ]
        mock_vision_client.return_value.text_detection.return_value = mock_response

        response = client.post(
            "/process-receipt",
            data={"receipt": mock_file},
            content_type="multipart/form-data",
            headers={"X-User-ID": "123"},
        )

        assert response.status_code == 200
        assert "text" in response.json
        assert "expense_id" in response.json

    def test_process_receipt_no_file(self, client):
        response = client.post(
            "/process-receipt", data={}, headers={"X-User-ID": "123"}
        )
        assert response.status_code == 400
        assert "error" in response.json

    def test_analyze_receipt_success(self, client, mock_vision_client):
        mock_file = (open("tests/test_data/sample_receipt.jpg", "rb"), "receipt.jpg")

        mock_response = Mock()
        mock_response.text_annotations = [
            Mock(description="Total: $100.00\nDate: 2023-12-01")
        ]
        mock_vision_client.return_value.text_detection.return_value = mock_response

        response = client.post(
            "/analyze-receipt",
            data={"receipt": mock_file},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert "data" in response.json
        assert "timestamp" in response.json

    def test_extract_expense_success(self, client):
        response = client.post(
            "/extract-expense", json={"text": "Total: $50.00\nDate: 2023-12-01"}
        )

        assert response.status_code == 200
        assert "expense" in response.json
        assert "timestamp" in response.json

    def test_extract_text_success(self, client, mock_vision_client):
        mock_file = (open("tests/test_data/sample_receipt.jpg", "rb"), "receipt.jpg")

        mock_response = Mock()
        mock_response.text_annotations = [Mock(description="Sample Receipt Text")]
        mock_vision_client.return_value.text_detection.return_value = mock_response

        response = client.post(
            "/extract-text",
            data={"receipt": mock_file},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert "text" in response.json
        assert "timestamp" in response.json

    def test_process_batch_success(self, client, mock_vision_client):
        mock_files = [
            (open("tests/test_data/receipt1.jpg", "rb"), "receipt1.jpg"),
            (open("tests/test_data/receipt2.jpg", "rb"), "receipt2.jpg"),
        ]

        response = client.post(
            "/process-batch",
            data={"receipts": mock_files},
            content_type="multipart/form-data",
            headers={"X-User-ID": "123"},
        )

        assert response.status_code == 202
        assert "batch_id" in response.json
        assert "status_endpoint" in response.json

    def test_batch_status_success(self, client):
        response = client.get("/batch-status/123")
        assert response.status_code == 200
        assert isinstance(response.json, dict)

    def test_rate_limit_exceeded(self, client):
        with patch("redis.Redis") as mock_redis:
            mock_redis.return_value.get.return_value = b"101"  # Over limit

            response = client.post(
                "/process-receipt",
                data={"receipt": "test"},
                headers={"X-User-ID": "123"},
            )

            assert response.status_code == 429
            assert "error" in response.json

    def test_invalid_file_type(self, client):
        mock_file = (open("tests/test_data/invalid.txt", "rb"), "invalid.txt")

        response = client.post(
            "/process-receipt",
            data={"receipt": mock_file},
            content_type="multipart/form-data",
            headers={"X-User-ID": "123"},
        )

        assert response.status_code == 400
        assert "error" in response.json

    def test_file_size_limit(self, client):
        # Create a large file that exceeds the limit
        large_file = b"0" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte

        response = client.post(
            "/process-receipt",
            data={"receipt": (large_file, "large.jpg")},
            content_type="multipart/form-data",
            headers={"X-User-ID": "123"},
        )

        assert response.status_code == 400
        assert "error" in response.json

    def test_ocr_confidence_score(self, client, mock_vision_client):
        mock_file = (open("tests/test_data/sample_receipt.jpg", "rb"), "receipt.jpg")

        mock_response = Mock()
        mock_response.text_annotations = [Mock(description="Test Receipt")]
        mock_response.full_text_annotation.pages = [Mock(confidence=0.95)]
        mock_vision_client.return_value.text_detection.return_value = mock_response

        response = client.post(
            "/process-receipt",
            data={"receipt": mock_file},
            content_type="multipart/form-data",
            headers={"X-User-ID": "123"},
        )

        assert response.status_code == 200
        assert "confidence_score" in response.json

    def test_receipt_data_extraction(self, client, mock_vision_client):
        mock_file = (open("tests/test_data/sample_receipt.jpg", "rb"), "receipt.jpg")

        # Mock detailed receipt data
        mock_response = Mock()
        mock_response.text_annotations = [
            Mock(description="Store: Test Store\nDate: 2023-12-01\nTotal: $150.00")
        ]
        mock_vision_client.return_value.text_detection.return_value = mock_response

        response = client.post(
            "/analyze-receipt",
            data={"receipt": mock_file},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        data = response.json["data"]
        assert "store" in data
        assert "date" in data
        assert "total" in data
