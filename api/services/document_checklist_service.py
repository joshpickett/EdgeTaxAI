from typing import Dict, Any, List
import logging
from datetime import datetime
from api.models.tax_forms import TaxForms, FormType
from api.services.mef.validation_rules import ValidationRules
from api.services.document_requirements_mapper import DocumentRequirementsMapper

class DocumentChecklistService:
    """Service for managing tax document requirements and checklists"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ValidationRules()
        self.requirements_mapper = DocumentRequirementsMapper()
        
        self.document_requirements = {
            'SCHEDULE_C': {
                'required': [
                    {'type': 'income_statement', 'priority': 'high'},
                    {'type': 'expense_receipts', 'priority': 'high'},
                    {'type': 'bank_statements', 'priority': 'medium'}
                ],
                'optional': [
                    {'type': 'vehicle_logs', 'priority': 'low'},
                    {'type': 'asset_purchase_records', 'priority': 'medium'}
                ]
            },
            '1099_NEC': {
                'required': [
                    {'type': '1099_nec_form', 'priority': 'high'},
                    {'type': 'contractor_agreement', 'priority': 'medium'}
                ],
                'optional': [
                    {'type': 'invoice_records', 'priority': 'low'}
                ]
            },
            'FORM_1116': {
                'required': [
                    {'type': 'foreign_tax_receipts', 'priority': 'high'},
                    {'type': 'foreign_income_statements', 'priority': 'high'}
                ],
                'optional': [
                    {'type': 'treaty_documentation', 'priority': 'medium'}
                ]
            },
            'SCHEDULE_C': {
                'required': [
                    {'type': 'foreign_bank_statements', 'priority': 'high'},
                    {'type': 'foreign_tax_returns', 'priority': 'high'},
                    {'type': 'foreign_income_docs', 'priority': 'high'}
                ],
                'optional': [
                    {'type': 'foreign_currency_docs', 'priority': 'medium'}
                ]
            }
        }

    async def generate_checklist(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Generate document checklist based on user's tax situation"""
        try:
            # Get user's answers and form types
            answers = await self._get_user_answers(user_id, tax_year)
            form_types = await self._get_user_form_types(user_id, tax_year)
             
            # Get required documents for each form type
            all_requirements = []
            for form_type in form_types:
                requirements = self.requirements_mapper.get_required_documents(form_type, answers)
                all_requirements.append(requirements)
            
            required_documents = []
            optional_documents = []
            for requirements in all_requirements:
                required_documents.extend(requirements.get('required', []))
                optional_documents.extend(requirements.get('optional', []))
            
            return {
                'required': self._prioritize_documents(required_documents),
                'optional': self._prioritize_documents(optional_documents),
                'status': self._get_document_status(user_id, required_documents)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating document checklist: {str(e)}")
            raise

    def _prioritize_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort documents by priority"""
        priority_scores = {'high': 3, 'medium': 2, 'low': 1}
        return sorted(
            documents,
            key=lambda x: priority_scores.get(x['priority'], 0),
            reverse=True
        )

    async def _get_document_status(
        self,
        user_id: int,
        required_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhanced document status check with international document support"""
        submitted_documents = await self._get_submitted_documents(user_id)
        
        status = {
            'total': len(required_documents),
            'submitted': 0,
            'missing': [],
            'incomplete': [],
            'international': {
                'required': [],
                'submitted': [],
                'missing': []
            }
        }
        
        for doc in required_documents:
            if self._is_international_document(doc['type']):
                status['international']['required'].append(doc['type'])
                if doc['type'] in submitted_documents:
                    status['international']['submitted'].append(doc['type'])
                else:
                    status['international']['missing'].append(doc['type'])
            else:
                if doc['type'] in submitted_documents:
                    status['submitted'] += 1
                else:
                    status['missing'].append(doc['type'])
                
        return status

    async def _get_user_tax_forms(self, user_id: int, tax_year: int) -> List[TaxForms]:
        """Get user's tax forms"""
        # Implementation would fetch actual tax forms
        # This is a placeholder
        return []

    async def _get_submitted_documents(self, user_id: int) -> List[str]:
        """Get list of submitted documents"""
        # Implementation would fetch actual submitted documents
        # This is a placeholder
        return []

    def _is_international_document(self, document_type: str) -> bool:
        """Check if the document type is international"""
        international_documents = [
            'foreign_bank_statements',
            'foreign_tax_returns',
            'foreign_income_docs',
            'foreign_tax_receipts',
            'foreign_income_statements',
            'foreign_currency_docs',
            'treaty_documentation'
        ]
        return document_type in international_documents
