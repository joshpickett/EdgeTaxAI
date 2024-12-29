from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class ScheduleCTemplate(BaseMeFTemplate):
    """Template for Schedule C XML generation"""
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Schedule C XML"""
        root = self.create_base_xml()
        self.add_header(root, data)
        
        # Add ScheduleC
        schedule_c = ElementTree.SubElement(root, 'IRS1040ScheduleC')
        
        # Business Information
        business_info = ElementTree.SubElement(schedule_c, 'BusinessInformation')
        self._add_business_info(business_info, data)
        
        # Income
        income = ElementTree.SubElement(schedule_c, 'Income')
        self._add_income_info(income, data)
        
        # Expenses
        expenses = ElementTree.SubElement(schedule_c, 'Expenses')
        self._add_expenses_info(expenses, data)
        
        xml_string = self.prettify_xml(root)
        
        # Validate against schema
        if not self.validate_xml(xml_string, 'schedule_c_2023v1.0.xsd'):
            raise ValueError("Generated XML failed schema validation")
            
        return xml_string
    
    def _add_business_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add business information section"""
        business_data = data.get('business_info', {})
        
        name = ElementTree.SubElement(parent, 'BusinessName')
        name.text = business_data.get('name', '')
        
        ein = ElementTree.SubElement(parent, 'EIN')
        ein.text = business_data.get('ein', '')
        
        address = ElementTree.SubElement(parent, 'BusinessAddress')
        self._add_address(address, business_data.get('address', {}))
        
    def _add_income_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add income information section"""
        income_data = data.get('income', {})
        
        gross_receipts = ElementTree.SubElement(parent, 'GrossReceipts')
        gross_receipts.text = str(income_data.get('gross_receipts', '0.00'))
        
        returns = ElementTree.SubElement(parent, 'ReturnsAndAllowances')
        returns.text = str(income_data.get('returns', '0.00'))
        
        other_income = ElementTree.SubElement(parent, 'OtherIncome')
        other_income.text = str(income_data.get('other_income', '0.00'))
        
    def _add_expenses_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add expenses information section"""
        expenses_data = data.get('expenses', {})
        
        expense_categories = {
            'Advertising': 'advertising',
            'CarAndTruck': 'car_and_truck',
            'CommissionsFees': 'commissions',
            'ContractLabor': 'contract_labor',
            'Depreciation': 'depreciation',
            'Insurance': 'insurance',
            'Interest': 'interest',
            'LegalServices': 'legal',
            'OfficeExpense': 'office',
            'Supplies': 'supplies',
            'Travel': 'travel',
            'Meals': 'meals',
            'Utilities': 'utilities'
        }
        
        for xml_name, data_key in expense_categories.items():
            expense = ElementTree.SubElement(parent, xml_name)
            expense.text = str(expenses_data.get(data_key, '0.00'))

    def _add_address(self, parent: ElementTree.Element, address_data: Dict[str, Any]) -> None:
        """Add address elements"""
        street = ElementTree.SubElement(parent, 'Street')
        street.text = address_data.get('street', '')
        
        city = ElementTree.SubElement(parent, 'City')
        city.text = address_data.get('city', '')
        
        state = ElementTree.SubElement(parent, 'State')
        state.text = address_data.get('state', '')
        
        zip_code = ElementTree.SubElement(parent, 'ZipCode')
        zip_code.text = address_data.get('zip_code', '')
