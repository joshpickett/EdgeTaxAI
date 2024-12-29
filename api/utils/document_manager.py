import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from api.utils.db_utils import get_db_connection
import json
import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from api.models.documents import Document, DocumentType, DocumentStatus
from api.config.database import get_db, engine

class DocumentError(Exception):
    """Base class for document-related errors"""
    pass

class DocumentValidationError(DocumentError):
    """Raised when document validation fails"""
    pass

class DocumentStorageError(DocumentError):
    """Raised when document storage fails"""
    pass

class DocumentManager:
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.document_store = "documents"
        self.logger = logging.getLogger(__name__)
        self._init_storage()
        
    def _init_storage(self):
        """Initialize document storage"""
        if not os.path.exists(self.document_store):
            os.makedirs(self.document_store)

    def validate_document(self, file_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate document before storage"""
        try:
            # Check file format
            file_ext = os.path.splitext(file_data['filename'])[1].lower()
            if file_ext not in self.supported_formats:
                return False, f"Unsupported file format. Allowed formats: {', '.join(self.supported_formats)}"

            # Check file size
            if file_data.get('size', 0) > self.max_file_size:
                return False, "File size exceeds maximum limit of 10MB"

            return True, "Valid document"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def store_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store document and metadata"""
        try:
            self._validate_user_permissions(data['user_id'])
            db = next(get_db())
            
            # Validate document
            is_valid, message = self.validate_document(data)
            if not is_valid:
                raise ValueError(message)

            user_id = data['user_id']
            document_type = data['type']
            content = data.get('content')
            metadata = data.get('metadata', {})
            tracking_id = str(uuid.uuid4())
            
            # Generate filename and store file
            file_path = self._store_file(content, data['filename'])
            
            document = Document(
                user_id=user_id,
                type=DocumentType(document_type),
                filename=data['filename'],
                file_path=file_path,
                metadata=json.dumps(metadata),
                status=DocumentStatus.PENDING
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return {
                'document_id': document.id,
                'filename': document.filename
            }
            
        except Exception as exception:
            self.logger.error(f"Error storing document: {exception}")
            raise DocumentStorageError(f"Error storing document: {str(exception)}")
            
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve document by ID"""
        try:
            with Session(engine) as session:
                document = session.query(Document).filter(
                    Document.id == document_id
                ).options(
                    joinedload(Document.user)
                ).first()
                
            if not document:
                return None
                
            return {
                'id': document.id,
                'user_id': document.user_id,
                'type': document.type.value,
                'filename': document.filename,
                'status': document.status.value,
                'metadata': json.loads(document.metadata) if document.metadata else {},
                'content': self._read_file(document.file_path),
                'created_at': document.created_at,
                'updated_at': document.updated_at
            }
            
        except Exception as exception:
            self.logger.error(f"Error retrieving document: {exception}")
            return None
            
    def get_user_documents(self, user_id: int, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        try:
            with Session(engine) as session:
                query = session.query(Document).filter(
                    Document.user_id == user_id
                ).options(
                    joinedload(Document.user)
                )
            
            if document_type:
                query = query.filter(Document.type == DocumentType(document_type))
                
            documents = query.all()
            
            return [{
                'id': document.id,
                'type': document.type.value,
                'filename': document.filename,
                'status': document.status.value,
                'metadata': json.loads(document.metadata) if document.metadata else {},
                'created_at': document.created_at
            } for document in documents]
            
        except Exception as exception:
            self.logger.error(f"Error retrieving user documents: {exception}")
            return []
            
    def delete_document(self, document_id: int) -> bool:
        """Delete document and its metadata"""
        try:
            db = next(get_db())
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return False
                
            # Delete from database
            db.delete(document)
            db.commit()
            
            # Delete file
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
                
            return True
            
        except Exception as exception:
            self.logger.error(f"Error deleting document: {exception}")
            return False

    def verify_document(self, document_id: int) -> Dict[str, Any]:
        """Verify document integrity and metadata"""
        try:
            document = self.get_document(document_id)
            if not document:
                raise DocumentError("Document not found")

            # Verify file exists
            if not os.path.exists(document['filename']):
                raise DocumentError("Document file missing")

            # Verify metadata integrity
            metadata = document.get('metadata', {})
            if not metadata.get('tracking_id'):
                raise DocumentError("Document tracking ID missing")

            # Update verification status
            self._update_document_status(document_id, 'verified')

            return {"status": "verified", "document": document}

        except Exception as e:
            self.logger.error(f"Document verification failed: {e}")
            raise DocumentError(f"Verification failed: {str(e)}")

    def _update_document_status(self, document_id: int, status: str) -> None:
        """Update the status of a document"""
        try:
            db = next(get_db())
            document = db.query(Document).filter(Document.id == document_id).first()
            document.status = DocumentStatus(status)
            db.commit()
        except Exception as e:
            self.logger.error(f"Error updating document status: {e}")
            raise DocumentError(f"Error updating document status: {str(e)}")

    def _store_file(self, content: Any, filename: str) -> str:
        file_path = os.path.join(self.document_store, filename)
        with open(file_path, 'w') as file:
            json.dump(content, file)
        return file_path

    def _read_file(self, file_path: str) -> Any:
        with open(file_path, 'r') as file:
            return json.load(file)

    def _validate_user_permissions(self, user_id: int) -> None:
        """Validate user permissions for document operations"""
        try:
            with Session(engine) as session:
                user = session.query(Users).filter(Users.id == user_id).first()
                if not user:
                    raise DocumentError("User not found")
                if not user.is_active:
                    raise DocumentError("User account is inactive")
        except Exception as e:
            raise DocumentError(f"Permission validation failed: {str(e)}")

    def _handle_db_error(self, operation: str, error: Exception) -> None:
        """Handle database operation errors"""
        self.logger.error(f"Database error during {operation}: {str(error)}")
        raise DocumentStorageError(f"Database operation failed: {str(error)}")
