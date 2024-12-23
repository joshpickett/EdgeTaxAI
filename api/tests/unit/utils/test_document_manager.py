import pytest
from unittest.mock import Mock, patch
from api.utils.document_manager import DocumentManager
from datetime import datetime

@pytest.fixture
def document_manager():
    return DocumentManager()

@pytest.fixture
def sample_document():
    return {
        'id': '123',
        'type': 'receipt',
        'content': b'sample content',
        'metadata': {
            'date': datetime.now().isoformat(),
            'category': 'expense'
        }
    }

def test_store_document_success(document_manager, sample_document):
    """Test successful document storage"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        result = document_manager.store_document(
            sample_document['content'],
            sample_document['type'],
            sample_document['metadata']
        )
        
        assert result['success'] is True
        assert 'document_id' in result
        mock_s3.upload_fileobj.assert_called_once()

def test_store_document_failure(document_manager, sample_document):
    """Test document storage failure"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.upload_fileobj.side_effect = Exception("Storage error")
        
        result = document_manager.store_document(
            sample_document['content'],
            sample_document['type'],
            sample_document['metadata']
        )
        
        assert result['success'] is False
        assert 'error' in result

def test_retrieve_document_success(document_manager):
    """Test successful document retrieval"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.get_object.return_value = {
            'Body': Mock(read=lambda: b'document content'),
            'Metadata': {'category': 'expense'}
        }
        
        result = document_manager.retrieve_document('123')
        
        assert result['success'] is True
        assert result['content'] == b'document content'
        assert result['metadata']['category'] == 'expense'

def test_retrieve_document_not_found(document_manager):
    """Test document retrieval when document not found"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.get_object.side_effect = Exception("Document not found")
        
        result = document_manager.retrieve_document('456')
        
        assert result['success'] is False
        assert 'error' in result

def test_delete_document_success(document_manager):
    """Test successful document deletion"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        result = document_manager.delete_document('123')
        
        assert result['success'] is True
        mock_s3.delete_object.assert_called_once()

def test_delete_document_failure(document_manager):
    """Test document deletion failure"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.delete_object.side_effect = Exception("Deletion error")
        
        result = document_manager.delete_document('123')
        
        assert result['success'] is False
        assert 'error' in result

def test_list_documents_success(document_manager):
    """Test successful document listing"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'doc1', 'LastModified': datetime.now()},
                {'Key': 'doc2', 'LastModified': datetime.now()}
            ]
        }
        
        result = document_manager.list_documents()
        
        assert result['success'] is True
        assert len(result['documents']) == 2

def test_list_documents_empty(document_manager):
    """Test listing documents when none exist"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.list_objects_v2.return_value = {}
        
        result = document_manager.list_documents()
        
        assert result['success'] is True
        assert len(result['documents']) == 0

def test_update_document_metadata_success(document_manager):
    """Test successful metadata update"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        new_metadata = {'category': 'updated_category'}
        result = document_manager.update_document_metadata('123', new_metadata)
        
        assert result['success'] is True
        mock_s3.copy_object.assert_called_once()

def test_update_document_metadata_failure(document_manager):
    """Test metadata update failure"""
    with patch('api.utils.document_manager.s3_client') as mock_s3:
        mock_s3.copy_object.side_effect = Exception("Update error")
        
        result = document_manager.update_document_metadata('123', {})
        
        assert result['success'] is False
        assert 'error' in result
