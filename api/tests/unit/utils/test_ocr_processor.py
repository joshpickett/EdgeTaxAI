import pytest
from unittest.mock import Mock, patch
from api.utils.ocr_processor import OCRProcessor
from google.cloud import vision

@pytest.fixture
def ocr_processor():
    return OCRProcessor()

@pytest.fixture
def mock_vision_client():
    with patch('google.cloud.vision.ImageAnnotatorClient') as mock:
        yield mock

@pytest.fixture
def sample_receipt_image():
    return b'mock_image_content'

@pytest.fixture
def mock_vision_response():
    mock_response = Mock()
    mock_response.text_annotations = [
        Mock(description="RECEIPT\nStore Name\n01/15/2023\nItem 1 $10.99\nItem 2 $5.99\nTOTAL $16.98")
    ]
    mock_response.full_text_annotation.pages = [Mock(confidence=0.95)]
    return mock_response

def test_process_receipt_success(ocr_processor, mock_vision_client, sample_receipt_image, mock_vision_response):
    """Test successful receipt processing"""
    mock_vision_client.return_value.text_detection.return_value = mock_vision_response
    
    result = ocr_processor.process_receipt(sample_receipt_image)
    
    assert result['date'] == '01/15/2023'
    assert result['total'] == 16.98
    assert result['vendor'] == 'Store Name'
    assert isinstance(result['items'], list)
    assert result['confidence_score'] > 0.9

def test_process_receipt_no_text(ocr_processor, mock_vision_client):
    """Test receipt processing with no text detected"""
    mock_response = Mock()
    mock_response.text_annotations = []
    mock_vision_client.return_value.text_detection.return_value = mock_response
    
    result = ocr_processor.process_receipt(b'empty_image')
    
    assert 'error' in result
    assert result['error'] == 'No text detected'

def test_extract_date_success(ocr_processor):
    """Test date extraction from text"""
    text = "Receipt\n01/15/2023\nOther text"
    date = ocr_processor._extract_date(text)
    assert date == '01/15/2023'

def test_extract_date_multiple_formats(ocr_processor):
    """Test date extraction with different formats"""
    dates = [
        "01/15/2023",
        "01-15-2023",
        "15 Jan 2023"
    ]
    
    for date_str in dates:
        text = f"Receipt\n{date_str}\nOther text"
        extracted = ocr_processor._extract_date(text)
        assert extracted is not None

def test_extract_total_success(ocr_processor):
    """Test total amount extraction"""
    text = "Items\n$10.99\nTOTAL $16.98"
    total = ocr_processor._extract_total(text)
    assert total == 16.98

def test_extract_total_multiple_formats(ocr_processor):
    """Test total extraction with different formats"""
    texts = [
        "TOTAL: $16.98",
        "Amount Due $16.98",
        "Total Due: $16.98"
    ]
    
    for text in texts:
        total = ocr_processor._extract_total(text)
        assert total == 16.98

def test_extract_vendor_success(ocr_processor):
    """Test vendor name extraction"""
    text = "Store Name\nOther text"
    vendor = ocr_processor._extract_vendor(text)
    assert vendor == "Store Name"

def test_extract_line_items_success(ocr_processor):
    """Test line items extraction"""
    text = "Item 1 $10.99\nItem 2 $5.99"
    items = ocr_processor._extract_line_items(text)
    assert len(items) == 2
    assert "Item 1 $10.99" in items

def test_calculate_confidence_success(ocr_processor, mock_vision_response):
    """Test confidence score calculation"""
    confidence = ocr_processor._calculate_confidence(mock_vision_response)
    assert confidence == 0.95

def test_error_handling(ocr_processor, mock_vision_client):
    """Test error handling during processing"""
    mock_vision_client.return_value.text_detection.side_effect = Exception("API Error")
    
    result = ocr_processor.process_receipt(b'image_content')
    
    assert 'error' in result
    assert 'API Error' in result['error']

def test_process_receipt_low_confidence(ocr_processor, mock_vision_client):
    """Test processing with low confidence score"""
    mock_response = Mock()
    mock_response.text_annotations = [Mock(description="Blurry text")]
    mock_response.full_text_annotation.pages = [Mock(confidence=0.3)]
    
    mock_vision_client.return_value.text_detection.return_value = mock_response
    
    result = ocr_processor.process_receipt(b'blurry_image')
    
    assert result['confidence_score'] < ocr_processor.confidence_threshold
