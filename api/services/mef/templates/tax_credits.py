from typing import Dict, Any
from decimal import Decimal

class TaxCreditCalculator:
    """Calculate various tax credits"""
    
    def calculate_child_tax_credit(self, data: Dict[str, Any]) -> Decimal:
        """Calculate Child Tax Credit"""
        num_qualifying_children = len(data.get('qualifying_children', []))
        base_amount = Decimal('2000.00') * num_qualifying_children
        
        # Apply income phase-out
        income = Decimal(str(data.get('adjusted_gross_income', 0)))
        if income > Decimal('200000'):  # Single filer threshold
            reduction = ((income - Decimal('200000')) / Decimal('1000')).quantize(Decimal('1.')) * Decimal('50')
            base_amount = max(Decimal('0'), base_amount - reduction)
            
        return base_amount
    
    def calculate_earned_income_credit(self, data: Dict[str, Any]) -> Decimal:
        """Calculate Earned Income Credit"""
        income = Decimal(str(data.get('earned_income', 0)))
        num_qualifying_children = len(data.get('qualifying_children', []))
        
        # Basic Earned Income Credit calculation (simplified)
        if num_qualifying_children == 0:
            max_credit = Decimal('560')
            phase_out_start = Decimal('9800')
        else:
            max_credit = Decimal('3600') * num_qualifying_children
            phase_out_start = Decimal('21000')
            
        if income > phase_out_start:
            reduction = ((income - phase_out_start) * Decimal('0.16')).quantize(Decimal('1.'))
            return max(Decimal('0'), max_credit - reduction)
            
        return max_credit
    
    def calculate_education_credits(self, data: Dict[str, Any]) -> Dict[str, Decimal]:
        """Calculate education-related credits"""
        qualified_expenses = Decimal(str(data.get('education_expenses', 0)))
        
        # American Opportunity Credit
        american_opportunity_credit = min(qualified_expenses, Decimal('4000')) * Decimal('0.25')
        
        # Lifetime Learning Credit
        lifetime_learning_credit = min(qualified_expenses, Decimal('10000')) * Decimal('0.2')
        
        return {
            'american_opportunity_credit': american_opportunity_credit,
            'lifetime_learning_credit': lifetime_learning_credit
        }
