from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from shared.types.tax_forms import Form1040Data, TaxFormType
from .base_template import BaseMeFTemplate
from .tax_calculator import TaxCalculationEngine
from .tax_credits import TaxCreditCalculator

class Form1040Template(BaseMeFTemplate):
    def __init__(self):
        super().__init__()
        self.form_type = TaxFormType.FORM_1040
        
    def generate(self, data: Form1040Data) -> str:
        """Generate Form 1040 XML using typed data"""
        # Implementation of XML generation goes here

    def _add_tax_and_credits(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add tax and credits section"""
        tax_data = data.get('tax_and_credits', {})
        income = Decimal(str(data.get('income', {}).get('total_income', '0')))
        filing_status = data.get('taxpayer', {}).get('filing_status')
         
        # Calculate tax using enhanced calculator
        tax_calculation = self.tax_calculator.calculate_tax_bracket(income, filing_status)
        tax = ElementTree.SubElement(parent, 'TaxAmount')
        tax.text = str(tax_calculation['total_tax'])

        # Additional implementation for credits can be added here

...rest of the code...
