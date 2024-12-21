import pytest
from unittest.mock import patch, MagicMock
from api.routes.ocr_routes import process_receipt, extract_text_from_image
import io

@pytest.fixture
def mock_vision_client():
    with patch('google.cloud.vision.ImageAnnotatorClient') as mock:
        yield mock

def test_process_receipt_success(mock_vision_client):
    mock_response = MagicMock()
    mock_response.text_annotations = [MagicMock(description="Test Receipt\nAmount: $50.00")]
    mock_vision_client.return_value.text_detection.return_value = mock_response
    
    # Create a mock file
    file_content = b"mock file content"
    mock_file = io.BytesIO(file_content)
    mock_file.filename = "receipt.jpg"
    
    result = process_receipt(mock_file)
    assert result["text"] == "Test Receipt\nAmount: $50.00"

def test_extract_text_invalid_image():
    with pytest.raises(Exception):
        extract_text_from_image(None)
