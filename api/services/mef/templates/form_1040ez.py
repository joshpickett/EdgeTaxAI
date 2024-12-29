from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate
from .tax_calculator import TaxCalculationEngine
from .tax_credits import TaxCreditCalculator

class Form1040EZTemplate(BaseMeFTemplate):
    def __init__(self):
        super().__init__()
        self.tax_calculator = TaxCalculationEngine()
        self.credit_calculator = TaxCreditCalculator()

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 1040-EZ XML"""

    def _add_tax_and_payments(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add tax and payments section"""
        tax_data = data.get('tax_and_payments', {})
        income = Decimal(str(data.get('income', {}).get('total_income', '0')))
        filing_status = data.get('taxpayer', {}).get('filing_status')
        
        # Calculate tax using enhanced calculator
        tax_calculation = self.tax_calculator.calculate_tax_bracket(income, filing_status)
        
        # Add tax amount
        tax = ElementTree.SubElement(parent, 'TaxAmount')
        tax.text = str(tax_calculation['total_tax'])
        
        # Add withholding
        withheld = ElementTree.SubElement(parent, 'FederalWithheld')
        withheld.text = str(tax_data.get('federal_withheld', '0.00'))
        
        # Calculate and add EIC if eligible
        eic_calculation = self.credit_calculator.calculate_earned_income_credit(data)
        eic = ElementTree.SubElement(parent, 'EarnedIncomeCredit')
        eic.text = str(eic_calculation)

...rest of the code...
