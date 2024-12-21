from decimal import Decimal
from typing import List, Tuple, Dict, Any
import logging

class TaxCalculator:
    def __init__(self, tax_brackets: List[Tuple[Decimal, Decimal, Decimal]]):
        self.tax_brackets = tax_brackets
        
    def calculate_progressive_tax(self, income: Decimal) -> Dict[str, Decimal]:
        """Calculate tax using progressive tax brackets"""
        total_tax = Decimal('0')
        bracket_taxes = []
        
        for i, (lower, upper, rate) in enumerate(self.tax_brackets):
            if income <= lower:
                break
                
            taxable_in_bracket = min(income - lower, upper - lower)
            if taxable_in_bracket > 0:
                tax_in_bracket = taxable_in_bracket * rate
                total_tax += tax_in_bracket
                bracket_taxes.append({
                    'bracket': i + 1,
                    'amount': taxable_in_bracket,
                    'rate': rate,
                    'tax': tax_in_bracket
                })
                
        return {
            'total_tax': total_tax,
            'effective_rate': total_tax / income if income > 0 else Decimal('0'),
            'bracket_breakdown': bracket_taxes
        }
        
    def calculate_quarterly_payment(self, annual_tax: Decimal) -> Decimal:
        """Calculate quarterly estimated tax payment"""
        return (annual_tax / Decimal('4')).quantize(Decimal('0.01'))
        
    def calculate_deduction_savings(self, income: Decimal, deduction: Decimal) -> Dict[str, Decimal]:
        """Calculate tax savings from a deduction"""
        tax_without = self.calculate_progressive_tax(income)
        tax_with = self.calculate_progressive_tax(income - deduction)
        
        savings = tax_without['total_tax'] - tax_with['total_tax']
        return {
            'deduction_amount': deduction,
            'tax_savings': savings,
            'effective_savings_rate': (savings / deduction).quantize(Decimal('0.0001'))
        }
