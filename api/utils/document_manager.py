import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import sqlite3
import json
import os
import uuid

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
    def __init__(self, database_path: str = "database.db"):
        self.database_path = database_path
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.document_store = "documents"
        self.logger = logging.getLogger(__name__)
        self._init_storage()
        
    def _init_storage(self):
        """Initialize document storage"""
        if not os.path.exists(self.document_store):
            os.makedirs(self.document_store)
            
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                filename TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'pending',
                tracking_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        connection.commit()
        connection.close()
        
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
            # Validate document
            is_valid, message = self.validate_document(data)
            if not is_valid:
                raise ValueError(message)

            user_id = data['user_id']
            document_type = data['type']
            content = data.get('content')
            metadata = data.get('metadata', {})
            tracking_id = str(uuid.uuid4())
            
            # Generate standardized filename
            file_ext = os.path.splitext(data['filename'])[1].lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}/{document_type}/{timestamp}{file_ext}"
            
            # Store document content
            metadata['tracking_id'] = tracking_id
            file_path = os.path.join(self.document_store, filename)
            with open(file_path, 'w') as file:
                json.dump(content, file)
            
            # Store metadata in database
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO documents (user_id, type, filename, metadata, tracking_id)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, document_type, filename, json.dumps(metadata), tracking_id))
            
            document_id = cursor.lastrowid
            connection.commit()
            connection.close()
            
            return {
                'document_id': document_id,
                'filename': filename
            }
            
        except Exception as exception:
            self.logger.error(f"Error storing document: {exception}")
            raise DocumentStorageError(f"Error storing document: {str(exception)}")
            
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve document by ID"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT * FROM documents WHERE id = ?
            """, (document_id,))
            
            document = cursor.fetchone()
            if not document:
                return None
                
            # Read document content
            filename = document[3]
            file_path = os.path.join(self.document_store, filename)
            with open(file_path, 'r') as file:
                content = json.load(file)
                
            return {
                'id': document[0],
                'user_id': document[1],
                'type': document[2],
                'filename': document[3],
                'metadata': json.loads(document[4]) if document[4] else {},
                'content': content,
                'created_at': document[5]
            }
            
        except Exception as exception:
            self.logger.error(f"Error retrieving document: {exception}")
            return None
            
    def get_user_documents(self, user_id: int, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            query = "SELECT * FROM documents WHERE user_id = ?"
            parameters = [user_id]
            
            if document_type:
                query += " AND type = ?"
                parameters.append(document_type)
                
            cursor.execute(query, parameters)
            documents = cursor.fetchall()
            
            return [{
                'id': document[0],
                'type': document[2],
                'filename': document[3],
                'metadata': json.loads(document[4]) if document[4] else {},
                'created_at': document[5]
            } for document in documents]
            
        except Exception as exception:
            self.logger.error(f"Error retrieving user documents: {exception}")
            return []
            
    def delete_document(self, document_id: int) -> bool:
        """Delete document and its metadata"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            # Get filename before deletion
            cursor.execute("SELECT filename FROM documents WHERE id = ?", (document_id,))
            document = cursor.fetchone()
            if not document:
                return False
                
            filename = document[0]
            
            # Delete from database
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            connection.commit()
            
            # Delete file
            file_path = os.path.join(self.document_store, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                
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
            file_path = os.path.join(self.document_store, document['filename'])
            if not os.path.exists(file_path):
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
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            cursor.execute("UPDATE documents SET status = ? WHERE id = ?", (status, document_id))
            connection.commit()
            connection.close()
        except Exception as e:
            self.logger.error(f"Error updating document status: {e}")
            raise DocumentError(f"Error updating document status: {str(e)}")
