from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form1116Template(BaseMeFTemplate):
    """Template for Form 1116 (Foreign Tax Credit) XML generation"""
    
    def __init__(self):
        super().__init__()
        self.form_type = 'Form1116'

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 1116 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)
        
        # Add Form 1116 with enhanced credit calculations
        form = ElementTree.SubElement(root, 'Form1116')
        
        # Add category selection
        category = ElementTree.SubElement(form, 'Category')
        category.text = data.get('category', '')
        
        # Add foreign source income with detailed breakdowns
        income = ElementTree.SubElement(form, 'ForeignSourceIncome')
        self._add_foreign_source_income(income, data.get('income', {}))
        
        # Add foreign taxes paid
        taxes = ElementTree.SubElement(form, 'ForeignTaxesPaid')
        self._add_foreign_taxes(taxes, data.get('taxes', {}))
        
        # Add credit calculation
        calculation = ElementTree.SubElement(form, 'CreditCalculation')
        self._add_credit_calculation(calculation, data.get('calculation', {}))
        
        xml_string = self.prettify_xml(root)
        
        # Validate against schema
        if not self.validate_xml(xml_string, '1116_2023v1.0.xsd'):
            raise ValueError("Generated XML failed schema validation")
            
        return xml_string

    def _add_foreign_source_income(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add foreign source income information"""
        gross_income = ElementTree.SubElement(parent, 'GrossIncome')
        gross_income.text = str(data.get('gross_income', '0.00'))
        
        deductions = ElementTree.SubElement(parent, 'Deductions')
        deductions.text = str(data.get('deductions', '0.00'))
        
        net_income = ElementTree.SubElement(parent, 'NetIncome')
        net_income.text = str(data.get('net_income', '0.00'))

    def _add_foreign_taxes(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add foreign taxes information"""
        # Add detailed tax breakdown by country
        countries = data.get('countries', [])
        for country_data in countries:
            country = ElementTree.SubElement(parent, 'Country')
            
            name = ElementTree.SubElement(country, 'Name')
            name.text = country_data.get('name', '')
            
            taxes = ElementTree.SubElement(country, 'Taxes')
            self._add_country_taxes(taxes, country_data.get('taxes', {}))

    def _add_credit_calculation(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add credit calculation information"""
        total_foreign_taxes = ElementTree.SubElement(parent, 'TotalForeignTaxes')
        total_foreign_taxes.text = str(data.get('total_foreign_taxes', '0.00'))
        
        credit_limit = ElementTree.SubElement(parent, 'CreditLimit')
        credit_limit.text = str(data.get('credit_limit', '0.00'))
        
        allowable_credit = ElementTree.SubElement(parent, 'AllowableCredit')
        allowable_credit.text = str(data.get('allowable_credit', '0.00'))
