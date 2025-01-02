from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import streamlit as streamlit
import requests
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from desktop.config import API_CONFIG


class DocumentManager:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.supported_formats = [".pdf", ".jpg", ".jpeg", ".png"]

    def process_document_upload(self, file, document_type: str, user_id: int) -> bool:
        """Process and upload tax document"""
        try:
            # Validate file
            if not self._validate_file(file):
                streamlit.error("Invalid file format or size")
                return False

            # Prepare upload
            files = {"file": file}
            data = {
                "user_id": user_id,
                "document_type": document_type,
                "upload_date": datetime.now().isoformat(),
            }

            # Upload to API
            response = requests.post(
                f"{self.api_base_url}/documents/upload", files=files, data=data
            )

            if response.status_code == 200:
                streamlit.success("Document uploaded successfully!")
                return True
            else:
                streamlit.error("Failed to upload document")
                return False

        except Exception as exception:
            logging.error(f"Document upload error: {exception}")
            streamlit.error("An error occurred during upload")
            return False

    def get_documents(
        self,
        user_id: int,
        year: Optional[int] = None,
        document_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve user's tax documents"""
        try:
            params = {"user_id": user_id}
            if year:
                params["year"] = year
            if document_type:
                params["document_type"] = document_type

            response = requests.get(f"{self.api_base_url}/documents", params=params)

            if response.status_code == 200:
                return response.json().get("documents", [])
            return []

        except Exception as exception:
            logging.error(f"Error fetching documents: {exception}")
            return []

    def download_document(self, document_id: str) -> Optional[bytes]:
        """Download specific document"""
        try:
            response = requests.get(
                f"{self.api_base_url}/documents/download/{document_id}"
            )

            if response.status_code == 200:
                return response.content
            return None

        except Exception as exception:
            logging.error(f"Document download error: {exception}")
            return None

    def _validate_file(self, file) -> bool:
        """Validate file format and size"""
        if not file:
            return False

        # Check format
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in self.supported_formats:
            return False

        # Check size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            return False

        return True
