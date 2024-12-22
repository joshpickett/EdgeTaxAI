from decimal import Decimal
from typing import Dict, Any
import logging
from datetime import datetime

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
            # Calculate immediate tax impact
            immediate_savings = self._calculate_progressive_tax(amount)
            
            # Project annual savings
            annual_savings = self._project_annual_savings(amount)
            
            # Calculate effective rate
            effective_rate = (immediate_savings / amount) if amount > 0 else 0
            
            return {
                'immediate_savings': float(immediate_savings),
                'annual_projection': float(annual_savings),
                'effective_rate': float(effective_rate),
                'calculated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error calculating tax savings: {e}")
            return {'immediate_savings': 0, 'annual_projection': 0, 'effective_rate': 0}
            
    def calculate_quarterly_tax(self, income: Decimal, expenses: Decimal) -> Dict[str, Any]:
        """Calculate quarterly estimated tax payments"""
        try:
            taxable_income = max(Decimal('0'), income - expenses)
            annual_tax = self._calculate_progressive_tax(taxable_income)
            quarterly_tax = annual_tax / Decimal('4')
            
            effective_rate = (annual_tax / taxable_income) if taxable_income > 0 else 0
            
            return {
                'quarterly_amount': float(quarterly_tax),
                'annual_tax': float(annual_tax),
                'effective_rate': float(effective_rate)
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
    
    def _project_annual_savings(self, current_amount: Decimal) -> Decimal:
        """Project annual tax savings based on current amount"""
        try:
            # Extrapolate to annual amount
            annual_projection = current_amount * Decimal('12')
            
            # Calculate tax savings on projected amount
            projected_savings = self._calculate_progressive_tax(annual_projection)
            
            # Apply confidence factor based on time of year
            current_month = datetime.now().month
            confidence_factor = Decimal(str(current_month / 12))
            
            return projected_savings * confidence_factor
        except Exception as e:
            logging.error(f"Error projecting annual savings: {e}")
            return Decimal('0')
