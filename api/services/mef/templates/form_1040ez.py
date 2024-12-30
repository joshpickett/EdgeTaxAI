from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from shared.types.tax_forms import Form1040EZData, TaxFormType
from .base_template import BaseMeFTemplate
from .tax_calculator import TaxCalculationEngine
from .tax_credits import TaxCreditCalculator

class Form1040EZTemplate(BaseMeFTemplate):
    def __init__(self):
        super().__init__()
        self.form_type = TaxFormType.FORM_1040EZ
        
    def generate(self, data: Form1040EZData) -> str:
        """Generate Form 1040-EZ XML using typed data"""
        root = self.create_base_xml()
        self.add_header(root, {'tax_year': 2023, 'form_type': 'Form1040EZ'})

        # Add Form1040EZ
        form = ElementTree.SubElement(root, 'Form1040EZ')
        
        # Add taxpayer information
        taxpayer = ElementTree.SubElement(form, 'TaxpayerInfo')
        self._add_taxpayer_info(taxpayer, data.taxpayerInfo)
        
        # Add income section
        income = ElementTree.SubElement(form, 'Income')
        self._add_income(income, data.income)
        
        # Add payments section
        payments = ElementTree.SubElement(form, 'Payments')
        self._add_payments(payments, data.payments)
        
        # Add calculations
        calculations = ElementTree.SubElement(form, 'Calculations')
        self._add_calculations(calculations, data.calculations)
        
        xml_string = self.prettify_xml(root)
        
        # Validate against schema
        if not self.validate_xml(xml_string, '1040ez_2023v1.0.xsd'):
            raise ValueError("Generated XML failed schema validation")
            
        return xml_string

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

    def _add_taxpayer_info(self, parent: ElementTree.Element, taxpayer_info: Dict[str, Any]) -> None:
        """Add taxpayer information section"""
        name = ElementTree.SubElement(parent, 'Name')
        name.text = f"{taxpayer_info['firstName']} {taxpayer_info['lastName']}"
        
        ssn = ElementTree.SubElement(parent, 'SSN')
        ssn.text = taxpayer_info['ssn']
        
        filing_status = ElementTree.SubElement(parent, 'FilingStatus')
        filing_status.text = taxpayer_info['filingStatus']

    def _add_income(self, parent: ElementTree.Element, income: Dict[str, Any]) -> None:
        """Add income section"""
        wages = ElementTree.SubElement(parent, 'Wages')
        wages.text = str(income['wages'])
        
        interest = ElementTree.SubElement(parent, 'Interest')
        interest.text = str(income['interest'])
        
        unemployment = ElementTree.SubElement(parent, 'UnemploymentCompensation')
        unemployment.text = str(income['unemploymentCompensation'])
        
        total = ElementTree.SubElement(parent, 'TotalIncome')
        total.text = str(income['totalIncome'])

    def _add_payments(self, parent: ElementTree.Element, payments: Dict[str, Any]) -> None:
        """Add payments section"""
        withheld = ElementTree.SubElement(parent, 'FederalTaxWithheld')
        withheld.text = str(payments['federalTaxWithheld'])
        
        earned_income_credit = ElementTree.SubElement(parent, 'EarnedIncomeCredit')
        earned_income_credit.text = str(payments['earnedIncomeCredit'])
        
        total = ElementTree.SubElement(parent, 'TotalPayments')
        total.text = str(payments['totalPayments'])

    def _add_calculations(self, parent: ElementTree.Element, calculations: Dict[str, Any]) -> None:
        """Add calculations section"""
        adjusted_gross_income = ElementTree.SubElement(parent, 'AdjustedGrossIncome')
        adjusted_gross_income.text = str(calculations['adjustedGrossIncome'])
        
        taxable_income = ElementTree.SubElement(parent, 'TaxableIncome')
        taxable_income.text = str(calculations['taxableIncome'])
        
        total_tax = ElementTree.SubElement(parent, 'TotalTax')
        total_tax.text = str(calculations['totalTax'])

...rest of the code...
