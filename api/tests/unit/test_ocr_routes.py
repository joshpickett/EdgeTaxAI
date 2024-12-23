import pytest
from flask import Flask
from ...routes.ocr_routes import ocr_bp
from unittest.mock import patch, MagicMock
import io

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(ocr_bp)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_process_receipt(client):
    """Test receipt processing endpoint"""
    with patch('api.routes.ocr_routes.vision') as mock_vision, \
         patch('api.routes.ocr_routes.expense_integration') as mock_expense:
        
        # Mock Vision API response
        mock_text = MagicMock()
        mock_text.description = "Test Receipt\nAmount: $50.00"
        mock_vision.ImageAnnotatorClient().text_detection.return_value.text_annotations = [mock_text]
        
        # Create test file
        data = {'receipt': (io.BytesIO(b"test"), 'test_receipt.jpg')}
        
        response = client.post('/process-receipt', 
                             content_type='multipart/form-data',
                             data=data,
                             headers={'X-User-ID': '1'})
        
        assert response.status_code == 200
        assert 'text' in response.get_json()

def test_process_receipt_no_file(client):
    """Test receipt processing without file"""
    response = client.post('/process-receipt',
                          content_type='multipart/form-data',
                          headers={'X-User-ID': '1'})
    
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_analyze_receipt(client):
    """Test receipt analysis endpoint"""
    with patch('api.routes.ocr_routes.vision') as mock_vision, \
         patch('api.routes.ocr_routes.extract_receipt_data') as mock_extract:
        
        # Mock Vision API response
        mock_text = MagicMock()
        mock_text.description = "Test Receipt\nAmount: $50.00"
        mock_vision.ImageAnnotatorClient().text_detection.return_value.text_annotations = [mock_text]
        
        # Mock extraction results
        mock_extract.return_value = {
            'amount': 50.00,
            'date': '2023-01-01',
            'vendor': 'Test Store'
        }
        
        data = {'receipt': (io.BytesIO(b"test"), 'test_receipt.jpg')}
        
        response = client.post('/analyze-receipt',
                             content_type='multipart/form-data',
                             data=data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert data['data']['amount'] == 50.00

def test_extract_expense(client):
    """Test expense extraction endpoint"""
    with patch('api.routes.ocr_routes.extract_receipt_data') as mock_extract:
        mock_extract.return_value = {
            'amount': 50.00,
            'category': 'office_supplies'
        }
        
        response = client.post('/extract-expense',
                             json={'text': 'Office supplies receipt $50.00'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'expense' in data
        assert data['expense']['amount'] == 50.00

def test_process_batch(client):
    """Test batch processing endpoint"""
    with patch('api.routes.ocr_routes.batch_processor') as mock_processor:
        mock_processor.process_batch.return_value = 'batch123'
        
        data = {
            'receipts': [
                (io.BytesIO(b"test1"), 'receipt1.jpg'),
                (io.BytesIO(b"test2"), 'receipt2.jpg')
            ]
        }
        
        response = client.post('/process-batch',
                             content_type='multipart/form-data',
                             data=data,
                             headers={'X-User-ID': '1'})
        
        assert response.status_code == 202
        assert 'batch_id' in response.get_json()
