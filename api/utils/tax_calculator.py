from decimal import Decimal
from typing import Dict, Any
import logging

class TaxCalculator:
    """Centralized tax calculation utility"""
    
    TAX_BRACKETS = [
        (Decimal('0'), Decimal('11000'), Decimal('0.10')),
        (Decimal('11000'), Decimal('44725'), Decimal('0.12')),
        (Decimal('44725'), Decimal('95375'), Decimal('0.22')),
        (Decimal('95375'), Decimal('182100'), Decimal('0.24')),
        (Decimal('182100'), Decimal('231250'), Decimal('0.32')),
        (Decimal('231250'), Decimal('578125'), Decimal('0.35')),
        (Decimal('578125'), Decimal('inf'), Decimal('0.37'))
    ]
    
    def calculate_tax_savings(self, amount: Decimal) -> Dict[str, Any]:
        """Calculate potential tax savings"""
        try:
            tax_due = self._calculate_progressive_tax(amount)
            return {
                'tax_savings': float(tax_due),
                'effective_rate': float(tax_due / amount) if amount > 0 else 0
            }
        except Exception as e:
            logging.error(f"Error calculating tax savings: {e}")
            return {'tax_savings': 0, 'effective_rate': 0}
            
    def calculate_quarterly_tax(self, income: Decimal, expenses: Decimal) -> Dict[str, Any]:
        """Calculate quarterly estimated tax payments"""
        try:
            taxable_income = max(Decimal('0'), income - expenses)
            annual_tax = self._calculate_progressive_tax(taxable_income)
            quarterly_tax = annual_tax / Decimal('4')
            
            return {
                'quarterly_amount': float(quarterly_tax),
                'annual_tax': float(annual_tax),
                'effective_rate': float(annual_tax / taxable_income) if taxable_income > 0 else 0
            }
        except Exception as e:
            logging.error(f"Error calculating quarterly tax: {e}")
            return {'quarterly_amount': 0, 'annual_tax': 0, 'effective_rate': 0}
            
    def _calculate_progressive_tax(self, income: Decimal) -> Decimal:
        """Calculate tax using progressive tax brackets"""
        total_tax = Decimal('0')
        
        for lower, upper, rate in self.TAX_BRACKETS:
            if income <= lower:
                break
                
            taxable_in_bracket = min(income - lower, upper - lower)
            if taxable_in_bracket > 0:
                total_tax += taxable_in_bracket * rate
                
        return total_tax
