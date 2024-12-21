import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3
import json
import os

class DocumentManager:
    def __init__(self, database_path: str = "database.db"):
        self.database_path = database_path
        self.document_store = "documents"
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        connection.commit()
        connection.close()
        
    def store_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store document and metadata"""
        try:
            user_id = data['user_id']
            document_type = data['type']
            content = data.get('content')
            metadata = data.get('metadata', {})
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}_{document_type}_{timestamp}.json"
            
            # Store document content
            file_path = os.path.join(self.document_store, filename)
            with open(file_path, 'w') as file:
                json.dump(content, file)
            
            # Store metadata in database
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO documents (user_id, type, filename, metadata)
                VALUES (?, ?, ?, ?)
            """, (user_id, document_type, filename, json.dumps(metadata)))
            
            document_id = cursor.lastrowid
            connection.commit()
            connection.close()
            
            return {
                'document_id': document_id,
                'filename': filename
            }
            
        except Exception as exception:
            logging.error(f"Error storing document: {exception}")
            raise
            
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
            logging.error(f"Error retrieving document: {exception}")
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
            logging.error(f"Error retrieving user documents: {exception}")
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
            logging.error(f"Error deleting document: {exception}")
            return False
