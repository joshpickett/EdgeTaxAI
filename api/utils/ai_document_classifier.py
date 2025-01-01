from typing import Dict, Any, Tuple
import logging
import json
from decimal import Decimal
from api.utils.ai_utils import get_ai_client

class DocumentClassifier:
    def __init__(self):
        self.ai_client = get_ai_client()
        self.logger = logging.getLogger(__name__)
        self.classification_rules = {
            'INCOME': {
                'keywords': ['salary', 'wages', 'compensation', 'dividend', 'interest'],
                'patterns': [r'W-?2', r'1099-[A-Z]{3}', r'K-?1']
            },
            'EXPENSE': {
                'keywords': ['payment', 'invoice', 'receipt', 'bill'],
                'patterns': [r'invoice#', r'receipt#', r'bill#']
            },
            'INTERNATIONAL': {
                'keywords': ['foreign', 'international', 'overseas'],
                'patterns': [r'FBAR', r'Form 8938', r'Form 5471']
            }
        }

    def classify_document(self, text_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify document type and determine category
        """
        try:
            classification_result = {
                'document_type': None,
                'category': None,
                'confidence': 0.0,
                'metadata': {},
                'suggestions': []
            }

            # Enhanced classification
            doc_type, confidence = self._detect_document_type(text_content, metadata)
            category = self._determine_category(doc_type, text_content)
            
            classification_result.update({
                'document_type': doc_type,
                'category': category,
                'confidence': confidence,
                'metadata': self._extract_metadata(text_content, doc_type)
            })

            return classification_result

        except Exception as e:
            self.logger.error(f"Document classification failed: {e}")
            return {
                'document_type': 'OTHER',
                'category': 'UNKNOWN',
                'confidence': 0.0,
                'metadata': {},
                'suggestions': []
            }

    def _detect_document_type(self, text_content: str, metadata: Dict[str, Any]) -> Tuple[str, float]:
        """Detect document type using AI analysis"""
        try:
            prompt = f"""Analyze this document text and classify it:
            1. Determine if it's an income document (W2, 1099, payment receipt) or
               expense document (bill, receipt, invoice) or other
            2. Identify specific document type
            3. Extract key financial information and dates
            4. Look for any special handling requirements
            5. Identify any international aspects

            Document text:
            {text_content[:500]}...
            
            Additional metadata:
            {json.dumps(metadata)}

            Respond in JSON format with classification, confidence, and metadata.
            """

            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document classification expert."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse AI response
            classification = response.choices[0].message.content
            result = json.loads(classification)

            return (
                result.get('document_type', 'OTHER'),
                result.get('confidence', 0.0)
            )

        except Exception as e:
            self.logger.error(f"Document type detection failed: {e}")
            return ('OTHER', 0.0)

    def _determine_category(self, doc_type: str, text_content: str) -> str:
        """Determine the category based on document type"""
        for category, rules in self.classification_rules.items():
            if any(keyword in text_content.lower() for keyword in rules['keywords']):
                return category
        return 'OTHER'

    def _extract_metadata(self, text_content: str, doc_type: str) -> Dict[str, Any]:
        """Extract metadata from the document"""
        # Placeholder for metadata extraction logic
        return {}
