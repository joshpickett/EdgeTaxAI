from typing import Dict, Any, List
import logging
from datetime import datetime
from api.models.tax_forms import TaxForms, FormType
from api.services.mef.validation_rules import ValidationRules

class DocumentChecklistService:
    """Service for managing tax document requirements and checklists"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ValidationRules()
        
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
            }
        }

    async def generate_checklist(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Generate document checklist based on user's tax situation"""
        try:
            tax_forms = await self._get_user_tax_forms(user_id, tax_year)
            required_documents = []
            optional_documents = []
            
            for form in tax_forms:
                requirements = self.document_requirements.get(form.form_type, {})
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
        """Get status of required documents"""
        submitted_documents = await self._get_submitted_documents(user_id)
        
        status = {
            'total': len(required_documents),
            'submitted': 0,
            'missing': [],
            'incomplete': []
        }
        
        for doc in required_documents:
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
