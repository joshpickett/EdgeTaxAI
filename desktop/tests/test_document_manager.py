import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from datetime import datetime
from desktop.document_manager import DocumentManager

@pytest.fixture
def document_manager():
    return DocumentManager("http://test-api")

@pytest.fixture
def mock_file():
    mock = Mock()
    mock.name = "test.pdf"
    mock.size = 1024 * 1024  # 1MB
    return mock

def test_process_document_upload_success(document_manager, mock_file):
    """Test successful document upload"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        
        result = document_manager.process_document_upload(
            mock_file,
            document_type="receipt",
            user_id=1
        )
        
        assert result is True
        mock_post.assert_called_once()

def test_process_document_upload_invalid_file(document_manager):
    """Test document upload with invalid file"""
    mock_file = Mock()
    mock_file.name = "test.txt"
    mock_file.size = 1024
    
    result = document_manager.process_document_upload(
        mock_file,
        document_type="receipt",
        user_id=1
    )
    
    assert result is False

def test_get_documents_success(document_manager):
    """Test successful document retrieval"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'documents': [{'id': 1, 'type': 'receipt'}]
        }
        
        documents = document_manager.get_documents(user_id=1)
        
        assert len(documents) == 1
        mock_get.assert_called_once()

def test_get_documents_with_filters(document_manager):
    """Test document retrieval with filters"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'documents': []}
        
        document_manager.get_documents(
            user_id=1,
            year=2023,
            document_type="receipt"
        )
        
        args = mock_get.call_args
        assert 'year' in args[1]['params']
        assert 'document_type' in args[1]['params']

def test_download_document_success(document_manager):
    """Test successful document download"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"test content"
        
        content = document_manager.download_document("doc123")
        
        assert content == b"test content"
        mock_get.assert_called_once()

def test_download_document_failure(document_manager):
    """Test document download failure"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        
        content = document_manager.download_document("doc123")
        
        assert content is None

def test_validate_file_size(document_manager, mock_file):
    """Test file size validation"""
    mock_file.size = 11 * 1024 * 1024  # 11MB
    
    assert document_manager._validate_file(mock_file) is False

def test_validate_file_format(document_manager, mock_file):
    """Test file format validation"""
    for ext in ['.pdf', '.jpg', '.jpeg', '.png']:
        mock_file.name = f"test{ext}"
        assert document_manager._validate_file(mock_file) is True
    
    mock_file.name = "test.txt"
    assert document_manager._validate_file(mock_file) is False
