import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from decimal import Decimal
from utils.db_utils import get_db_connection

def calculate_quarterly_tax(self, income: Decimal, expenses: Decimal) -> Dict[str, Any]:
    try:
        net_income = income - expenses
        # Enhanced deduction handling
        deductions = self._calculate_available_deductions(income, expenses)
        adjusted_income = net_income - deductions
        
        tax_breakdown = {
            'gross_income': float(income),
            'total_expenses': float(expenses),
            'total_deductions': float(deductions),
            'adjusted_income': float(adjusted_income),
            'quarterly_tax': float(self._calculate_quarterly_amount(adjusted_income)),
            'estimated_annual_tax': float(self._calculate_annual_tax(adjusted_income))
        }
        
        return tax_breakdown

...rest of the code...
