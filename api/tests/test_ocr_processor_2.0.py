import pytest
from unittest.mock import Mock, patch
from ..utils.ocr_processor import OCRProcessor
from google.cloud import vision

class TestOCRProcessor:
    @pytest.fixture
    def ocr_processor(self):
        return OCRProcessor()

    @pytest.fixture
    def mock_vision_client(self):
        with patch('google.cloud.vision.ImageAnnotatorClient') as mock:
            yield mock

    def test_process_receipt_success(self, ocr_processor, mock_vision_client):
        # Mock response from Vision Application Programming Interface
        mock_response = Mock()
        mock_response.text_annotations = [
            Mock(description="Test Store\nTotal: $50.00\nDate: 2023-12-01")
        ]
        mock_vision_client.return_value.text_detection.return_value = mock_response

        result = ocr_processor.process_receipt(b"fake_image_content")
        
        assert result['vendor'] == 'Test Store'
        assert result['total'] == 50.00
        assert result['date'] == '2023-12-01'
        assert result['confidence_score'] >= 0.0

    def test_process_receipt_no_text(self, ocr_processor, mock_vision_client):
        mock_response = Mock()
        mock_response.text_annotations = []
        mock_vision_client.return_value.text_detection.return_value = mock_response

        result = ocr_processor.process_receipt(b"fake_image_content")
        
        assert 'error' in result
        assert result['error'] == 'No text detected'

    def test_extract_date_multiple_formats(self, ocr_processor):
        date_texts = [
            "12/25/2023",
            "2023-12-25",
            "25 Dec 2023"
        ]
        
        for text in date_texts:
            result = ocr_processor._extract_date(text)
            assert result is not None

    def test_extract_total_multiple_formats(self, ocr_processor):
        total_texts = [
            "TOTAL: $123.45",
            "Amount Due: $123.45",
            "Total Due: $123.45"
        ]
        
        for text in total_texts:
            result = ocr_processor._extract_total(text)
            assert result == 123.45

    def test_calculate_confidence_score(self, ocr_processor):
        mock_response = Mock()
        mock_response.full_text_annotation.pages = [
            Mock(confidence=0.95),
            Mock(confidence=0.85)
        ]
        
        confidence = ocr_processor._calculate_confidence(mock_response)
        assert confidence == 0.90

    def test_extract_vendor_multiple_lines(self, ocr_processor):
        text = "Store Name\nAddress Line\nPhone Number"
        vendor = ocr_processor._extract_vendor(text)
        assert vendor == "Store Name"

    def test_extract_line_items(self, ocr_processor):
        text = "Item 1 $10.00\nItem 2 $20.00\nTotal: $30.00"
        items = ocr_processor._extract_line_items(text)
        assert len(items) == 3
        assert all('$' in item for item in items)

    def test_process_receipt_api_error(self, ocr_processor, mock_vision_client):
        mock_vision_client.return_value.text_detection.side_effect = Exception("Application Programming Interface Error")
        
        result = ocr_processor.process_receipt(b"fake_image_content")
        assert 'error' in result

    def test_extract_date_invalid_format(self, ocr_processor):
        text = "Invalid Date Format"
        result = ocr_processor._extract_date(text)
        assert result is None

    def test_extract_total_invalid_format(self, ocr_processor):
        text = "Invalid Total Format"
        result = ocr_processor._extract_total(text)
        assert result is None
