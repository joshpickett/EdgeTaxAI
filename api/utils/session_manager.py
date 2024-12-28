from api.setup_path import setup_python_path
setup_python_path(__file__)

import os
import logging
from datetime import datetime, timedelta
import uuid
import json
from typing import Optional, Dict, Any
from pathlib import Path

class SessionManager:
    def __init__(self, session_directory: str = ".sessions"):
        self.session_directory = Path(session_directory)
        self.session_duration = 86400  # 24 hours in seconds
        self._init_session_directory()
        self.sessions = {}  # In-memory cache of active sessions

    def _init_session_directory(self):
        """Initialize session directory"""
        os.makedirs(self.session_directory, exist_ok=True)
        
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
        
    def create_session(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Create new session for desktop user"""
        try:
            session_id = self.generate_session_id()
            session_data = {
                'user_id': user_id,
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=self.session_duration)).isoformat(),
                'data': data
            }
            
            session_file = self.session_directory / f"session_{session_id}.json"
            with open(session_file, 'w') as file:
                json.dump(session_data, file)
            self.sessions[session_id] = session_data
            return True
        except Exception as exception:
            logging.error(f"Error creating session: {exception}")
            return False
            
    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user session"""
        try:
            session_file = self.session_directory / f"session_{user_id}.json"
            if not session_file.exists():
                return None
                
            with open(session_file, 'r') as file:
                session_data = json.load(file)
                
            # Check expiration
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                self.delete_session(user_id)
                return None
                
            return session_data
        except Exception as exception:
            logging.error(f"Error retrieving session: {exception}")
            return None
            
    def update_session(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Update existing session data"""
        try:
            current_session = self.get_session(user_id)
            if not current_session:
                return False
                
            current_session['data'].update(data)
            current_session['updated_at'] = datetime.now().isoformat()
            
            session_file = self.session_directory / f"session_{current_session['session_id']}.json"
            with open(session_file, 'w') as file:
                json.dump(current_session, file)
            return True
        except Exception as exception:
            logging.error(f"Error updating session: {exception}")
            return False
            
    def delete_session(self, user_id: int) -> bool:
        """Delete user session"""
        try:
            session_file = self.session_directory / f"session_{user_id}.json"
            if session_file.exists():
                os.remove(session_file)
            return True
        except Exception as exception:
            logging.error(f"Error deleting session: {exception}")
            return False
            
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is active and not expired"""
        try:
            session_file = self.session_directory / f"session_{session_id}.json"
            if not session_file.exists():
                return False
                
            with open(session_file, 'r') as file:
                session_data = json.load(file)
                
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                return False
                
            return True
        except Exception as exception:
            logging.error(f"Error validating session: {exception}")
            return False
