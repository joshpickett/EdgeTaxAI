import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from typing import Dict, Any, List
from decimal import Decimal
from api.utils.db_utils import get_db_connection

class IRSCompliance:
    def __init__(self):
        self.compliance_rules = {
            'documentation_required': {
                'mileage': ['date', 'distance', 'purpose'],
                'meals': ['receipt', 'business_purpose', 'attendees'],
                'office_supplies': ['receipt', 'business_purpose'],
                'travel': ['receipt', 'business_purpose', 'destination']
            },
            'deduction_limits': {
                'meals': Decimal('0.50'),  # 50% deductible
                'gifts': Decimal('25.00'),  # $25 per person
                'home_office': Decimal('1500.00')  # Simplified option
            }
        }
        
    def verify_compliance(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if expense meets IRS compliance requirements"""
        category = expense.get('category', '').lower()
        # Enhanced compliance checks
        compliance_checks = {
            'documentation': self._check_documentation(expense),
            'amount_limits': self._check_amount_limits(expense),
            'timing': self._check_timing_requirements(expense),
            'business_purpose': self._verify_business_purpose(expense)
        }
        
        compliance_score = self._calculate_compliance_score(compliance_checks)
        
        required_docs = self.compliance_rules['documentation_required'].get(category, [])
        
        # Check required documentation
        missing_docs = [
            doc for doc in required_docs 
            if not expense.get(doc)
        ]
        
        # Calculate compliance score
        compliance_score = 1.0 - (len(missing_docs) / len(required_docs)) if required_docs else 1.0
        
        # Check deduction limits
        deduction_limit = self.compliance_rules['deduction_limits'].get(category)
        amount = Decimal(str(expense.get('amount', 0)))
        
        is_within_limits = True
        if deduction_limit:
            if category == 'meals':
                is_within_limits = True  # Meals are percentage based
                amount = amount * deduction_limit
            else:
                is_within_limits = amount <= deduction_limit
        
        return {
            'is_compliant': not missing_docs and is_within_limits,
            'compliance_score': compliance_score,
            'missing_documentation': missing_docs,
            'deductible_amount': float(amount),
            'within_limits': is_within_limits
        }
        
    def generate_audit_trail(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audit trail for expense"""
        return {
            'timestamp': expense.get('date'),
            'category': expense.get('category'),
            'amount': expense.get('amount'),
            'documentation': {
                'receipt': bool(expense.get('receipt')),
                'purpose': bool(expense.get('business_purpose')),
                'additional_docs': expense.get('additional_documentation', [])
            },
            'compliance_check': self.verify_compliance(expense)
        }
