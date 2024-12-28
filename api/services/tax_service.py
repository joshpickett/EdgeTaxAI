from typing import Dict, Any, List
from decimal import Decimal
import logging
from datetime import datetime
from api.config.tax_config import TAX_CONFIG
from api.utils.tax_calculator import TaxCalculator
from api.utils.cache_utils import CacheManager
from api.exceptions.tax_exceptions import TaxCalculationError

class TaxService:
    def __init__(self):
        self.calculator = TaxCalculator()
        self.cache = CacheManager()

    def estimate_quarterly_taxes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quarterly estimated taxes"""
        try:
            income = Decimal(str(data.get('income', 0)))
            expenses = Decimal(str(data.get('expenses', 0)))
            quarter = data.get('quarter')
            
            if not quarter or quarter not in TAX_CONFIG['QUARTERLY_DEADLINES']:
                raise ValueError("Invalid quarter specified")
                
            return self.calculator.calculate_quarterly_tax(income, expenses, quarter)
        except Exception as e:
            logging.error(f"Error calculating quarterly taxes: {str(e)}")
            raise TaxCalculationError(str(e))

    def analyze_deductions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze expenses for deductions"""
        try:
            expenses = data.get('expenses', [])
            if not expenses or not isinstance(expenses, list):
                raise ValueError("Invalid expenses data")
                
            return self.calculator.analyze_deductions(expenses)
        except Exception as e:
            logging.error(f"Error analyzing deductions: {str(e)}")
            raise TaxCalculationError(str(e))

    def calculate_tax_savings(self, amount: Decimal) -> Dict[str, Any]:
        """Calculate potential tax savings"""
        try:
            return {
                'savings': self.calculator.calculate_savings(amount),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error calculating tax savings: {str(e)}")
            raise TaxCalculationError(str(e))

    def generate_tax_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tax documents"""
        try:
            document_type = data.get('document_type')
            if document_type not in ['schedule_c', 'quarterly_estimate']:
                raise ValueError("Invalid document type")
                
            return self.calculator.generate_document(data)
        except Exception as e:
            logging.error(f"Error generating tax document: {str(e)}")
            raise TaxCalculationError(str(e))
