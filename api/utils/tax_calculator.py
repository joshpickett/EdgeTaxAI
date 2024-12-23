from typing import Dict, List, Optional
from decimal import Decimal
import logging

class TaxCalculator:
    def __init__(self):
        self.standard_mileage_rate = 0.655  # 2023 IRS rate
        self.tax_brackets = {
            'self_employment': 0.153,  # 15.3% self-employment tax
            'income_tax': {
                12550: 0.10,  # Standard deduction threshold
                22500: 0.12,
                58575: 0.22,
                109225: 0.24,
                195950: 0.32,
                245100: 0.35,
                591975: 0.37
            }
        }

    def calculate_mileage_deduction(self, total_miles: float) -> float:
        """Calculate mileage deduction based on IRS standard rate."""
        return round(float(total_miles * self.standard_mileage_rate), 2)

    def calculate_self_employment_tax(self, net_income: float) -> Dict[str, float]:
        """Calculate self-employment tax."""
        self_employment_tax_rate = self.tax_brackets['self_employment']
        self_employment_tax = round(net_income * self_employment_tax_rate, 2)
        return {
            'tax_amount': self_employment_tax,
            'tax_rate': self_employment_tax_rate
        }

    def calculate_income_tax(self, taxable_income: float) -> Dict[str, float]:
        """Calculate income tax based on progressive tax brackets."""
        total_tax = 0
        previous_bracket = 0
        effective_rate = 0

        for bracket, rate in sorted(self.tax_brackets['income_tax'].items()):
            if taxable_income > previous_bracket:
                taxable_amount = min(taxable_income - previous_bracket, bracket - previous_bracket)
                total_tax += taxable_amount * rate
                previous_bracket = bracket
            else:
                break

        if taxable_income > 0:
            effective_rate = total_tax / taxable_income

        return {
            'tax_amount': round(total_tax, 2),
            'effective_rate': round(effective_rate, 4)
        }

    def estimate_quarterly_taxes(self, income: float, expenses: float, 
                               mileage: float = 0) -> Dict[str, float]:
        """Estimate quarterly tax payments."""
        mileage_deduction = self.calculate_mileage_deduction(mileage)
        total_deductions = expenses + mileage_deduction
        net_income = max(0, income - total_deductions)

        self_employment_tax = self.calculate_self_employment_tax(net_income)
        income_tax = self.calculate_income_tax(net_income)

        quarterly_payment = (self_employment_tax['tax_amount'] + income_tax['tax_amount']) / 4

        return {
            'quarterly_payment': round(quarterly_payment, 2),
            'annual_tax_estimate': round(self_employment_tax['tax_amount'] + income_tax['tax_amount'], 2),
            'self_employment_tax': self_employment_tax['tax_amount'],
            'income_tax': income_tax['tax_amount'],
            'total_deductions': round(total_deductions, 2)
        }

    def get_tax_summary(self, annual_income: float, expenses: List[Dict], 
                       mileage: float) -> Dict[str, any]:
        """Generate comprehensive tax summary."""
        total_expenses = sum(expense['amount'] for expense in expenses)
        tax_estimate = self.estimate_quarterly_taxes(annual_income, total_expenses, mileage)
        
        return {
            'gross_income': round(annual_income, 2),
            'total_expenses': round(total_expenses, 2),
            'mileage_deduction': self.calculate_mileage_deduction(mileage),
            'net_income': round(annual_income - total_expenses - 
                              self.calculate_mileage_deduction(mileage), 2),
            'quarterly_tax_payments': tax_estimate['quarterly_payment'],
            'annual_tax_estimate': tax_estimate['annual_tax_estimate'],
            'effective_tax_rate': round(
                tax_estimate['annual_tax_estimate'] / annual_income * 100, 2
            ) if annual_income > 0 else 0
        }
