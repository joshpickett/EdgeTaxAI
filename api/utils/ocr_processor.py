import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from typing import Dict, Any, Optional
from google.cloud import vision
import re
from datetime import datetime


class OCRProcessor:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        self.confidence_threshold = 0.8

    def process_receipt(self, image_content: bytes) -> Dict[str, Any]:
        """Process receipt image and extract structured data"""
        try:
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)

            if not response.text_annotations:
                return {"error": "No text detected"}

            extracted_text = response.text_annotations[0].description

            # Extract key information
            data = {
                "date": self._extract_date(extracted_text),
                "total": self._extract_total(extracted_text),
                "vendor": self._extract_vendor(extracted_text),
                "items": self._extract_line_items(extracted_text),
                "confidence_score": self._calculate_confidence(response),
            }

            return data
        except Exception as e:
            logging.error(f"OCR processing error: {e}")
            return {"error": str(e)}

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text"""
        date_patterns = [
            r"\d{2}/\d{2}/\d{4}",
            r"\d{2}-\d{2}-\d{4}",
            r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from receipt"""
        total_patterns = [
            r"TOTAL[\s:]*\$?\s*(\d+\.\d{2})",
            r"Amount[\s:]*\$?\s*(\d+\.\d{2})",
            r"Due[\s:]*\$?\s*(\d+\.\d{2})",
        ]

        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_vendor(self, text: str) -> Optional[str]:
        """Extract vendor name from receipt"""
        lines = text.split("\n")
        if lines:
            return lines[0].strip()
        return None

    def _extract_line_items(self, text: str) -> list:
        """Extract individual line items from receipt"""
        items = []
        lines = text.split("\n")

        for line in lines:
            if re.search(r"\$\s*\d+\.\d{2}", line):
                items.append(line.strip())

        return items

    def _calculate_confidence(self, response) -> float:
        """Calculate overall confidence score"""
        if not response.text_annotations:
            return 0.0

        confidences = [page.confidence for page in response.full_text_annotation.pages]
        return sum(confidences) / len(confidences) if confidences else 0.0
