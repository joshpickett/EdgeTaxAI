from typing import Dict, Any, Tuple
import logging
import json
from decimal import Decimal
from api.utils.ai_utils import get_ai_client

class DocumentClassifier:
    def __init__(self):
        self.ai_client = get_ai_client()
        self.logger = logging.getLogger(__name__)

    def classify_document(self, text_content: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Classify document type and determine if it's income or expense related
        Returns: (document_type, confidence_score, metadata)
        """
        try:
            # Prepare prompt for classification
            prompt = f"""Analyze this document text and classify it:
            1. Determine if it's an income document (W2, 1099, payment receipt) or
               expense document (bill, receipt, invoice) or other
            2. Identify specific document type
            3. Extract key financial information

            Document text:
            {text_content[:500]}...

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
                result.get('confidence', 0.0),
                result.get('metadata', {})
            )

        except Exception as e:
            self.logger.error(f"Document classification failed: {e}")
            return ('OTHER', 0.0, {})

    def should_store_as_income(self, doc_type: str, metadata: Dict[str, Any]) -> bool:
        """Determine if document should be stored as income"""
        income_indicators = ['W2', '1099', 'PAYMENT', 'INCOME', 'SALARY']
        return any(indicator in doc_type.upper() for indicator in income_indicators)

    def should_store_as_expense(self, doc_type: str, metadata: Dict[str, Any]) -> bool:
        """Determine if document should be stored as expense"""
        expense_indicators = ['RECEIPT', 'INVOICE', 'BILL', 'EXPENSE']
        return any(indicator in doc_type.upper() for indicator in expense_indicators)

    def extract_financial_data(self, text_content: str, doc_type: str) -> Dict[str, Any]:
        """Extract financial data based on document type"""
        try:
            prompt = f"""Extract financial information from this {doc_type} document:
            For income documents:
            - Total income amount
            - Payment date
            - Payer information
            - Tax withholding (if any)

            For expense documents:
            - Total amount
            - Vendor name
            - Purchase date
            - Category

            Document text:
            {text_content[:500]}...

            Return as JSON with extracted fields.
            """

            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction expert."},
                    {"role": "user", "content": prompt}
                ]
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.logger.error(f"Financial data extraction failed: {e}")
            return {}
