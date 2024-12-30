from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from shared.types.tax_forms import Form1040Data, TaxFormType, FilingStatus
from .base_template import BaseMeFTemplate
from .tax_calculator import TaxCalculationEngine
from .tax_credits import TaxCreditCalculator

class Form1040Template(BaseMeFTemplate):
    def __init__(self):
        super().__init__()
        self.form_type = TaxFormType.FORM_1040
        self.tax_calculator = TaxCalculationEngine()
        self.credit_calculator = TaxCreditCalculator()
        
    def generate(self, data: Form1040Data) -> str:
        """Generate Form 1040 XML"""
        root = self.create_base_xml()
        self.add_header(root, {'tax_year': data.year, 'form_type': 'Form1040'})
        
        # Add Form1040
        form = ElementTree.SubElement(root, 'Form1040')
        
        # Add main sections
        self._add_taxpayer_info(form, data.taxpayerInfo)
        self._add_income(form, data.income)
        self._add_adjustments(form, data.adjustments)
        self._add_tax_and_credits(form, data)
        self._add_payments(form, data.payments)

    def _add_tax_and_credits(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add tax and credits section"""
        tax_section = ElementTree.SubElement(parent, 'TaxAndCredits')
        
        # Calculate tax
        income = Decimal(str(data.income.totalIncome))
        filing_status = data.taxpayerInfo.filingStatus
          
        # Calculate tax using enhanced calculator
        tax_calculation = self.tax_calculator.calculate_tax_bracket(income, filing_status)
        
        # Add tax amount
        tax = ElementTree.SubElement(tax_section, 'TaxAmount')
        tax.text = str(tax_calculation['total_tax'])
        
        # Add credits
        credits = ElementTree.SubElement(tax_section, 'Credits')
        
        # Child tax credit
        if data.credits.qualifyingChildren:
            child_credit = self.credit_calculator.calculate_child_tax_credit({
                'qualifying_children': data.credits.qualifyingChildren,
                'adjusted_gross_income': income
            })
            child_tax = ElementTree.SubElement(credits, 'ChildTaxCredit')
            child_tax.text = str(child_credit)

    def _add_income(self, parent: ElementTree.Element, income_data: Dict[str, Any]) -> None:
        """Add income section"""
        income = ElementTree.SubElement(parent, 'Income')
        
        # Wages
        wages = ElementTree.SubElement(income, 'Wages')
        wages.text = str(income_data.get('wages', '0.00'))
        
        # Interest
        interest = ElementTree.SubElement(income, 'Interest')
        interest.text = str(income_data.get('interest', '0.00'))
        
        # Business income
        business = ElementTree.SubElement(income, 'BusinessIncome')
        business.text = str(income_data.get('business', '0.00'))
        
        # Total income
        total = ElementTree.SubElement(income, 'TotalIncome')
        total.text = str(income_data.get('totalIncome', '0.00'))

    def _add_adjustments(self, parent: ElementTree.Element, adjustments_data: Dict[str, Any]) -> None:
        """Add adjustments to income section"""
        adjustments = ElementTree.SubElement(parent, 'Adjustments')
        
        # Self-employment tax deduction
        self_employment_tax = ElementTree.SubElement(adjustments, 'SelfEmploymentTax')
        self_employment_tax.text = str(adjustments_data.get('selfEmploymentTax', '0.00'))
        
        # Health insurance
        health = ElementTree.SubElement(adjustments, 'HealthInsurance')
        health.text = str(adjustments_data.get('healthInsurance', '0.00'))
        
        # Total adjustments
        total = ElementTree.SubElement(adjustments, 'TotalAdjustments')
        total.text = str(adjustments_data.get('totalAdjustments', '0.00'))

...rest of the code...
