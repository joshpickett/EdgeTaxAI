from typing import Dict, Any, List
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_schedule_template import BaseScheduleTemplate

class ScheduleFTemplate(BaseScheduleTemplate):
    """Template for Schedule F (Farming Income) XML generation"""
    
    def __init__(self):
        super().__init__()
        self.schedule_type = 'F'

    def _add_schedule_content(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Schedule F specific content"""
        # Add farm information
        farm_info = ElementTree.SubElement(parent, 'FarmInfo')
        self._add_farm_info(farm_info, data.get('farm_info', {}))
        
        # Add income section
        income = ElementTree.SubElement(parent, 'Income')
        self._add_income_info(income, data.get('income', {}))
        
        # Add expenses section
        expenses = ElementTree.SubElement(parent, 'Expenses')
        self._add_expense_info(expenses, data.get('expenses', {}))
        
        # Add depreciation
        depreciation = ElementTree.SubElement(parent, 'Depreciation')
        self._add_depreciation_info(depreciation, data.get('depreciation', {}))

    def _add_farm_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add farm information"""
        name = ElementTree.SubElement(parent, 'FarmName')
        name.text = data.get('name', '')
        
        address = ElementTree.SubElement(parent, 'FarmAddress')
        self._add_address(address, data.get('address', {}))
        
        principal_product = ElementTree.SubElement(parent, 'PrincipalProduct')
        principal_product.text = data.get('principal_product', '')
        
        accounting_method = ElementTree.SubElement(parent, 'AccountingMethod')
        accounting_method.text = data.get('accounting_method', 'Cash')

    def _add_income_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add income information"""
        income_categories = [
            'sales_livestock', 'sales_produce', 'cooperative_distributions',
            'agricultural_payments', 'commodity_payments', 'crop_insurance',
            'custom_hire', 'other_income'
        ]
        
        for category in income_categories:
            if category in data:
                elem = ElementTree.SubElement(parent, category.title())
                elem.text = str(data[category])
        
        total = ElementTree.SubElement(parent, 'TotalIncome')
        total.text = str(self._calculate_total_income(data))

    def _add_expense_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add expense information"""
        expense_categories = [
            'car_truck', 'chemicals', 'conservation', 'custom_hire',
            'depreciation', 'employee_benefit', 'feed', 'fertilizers',
            'freight', 'fuel', 'insurance', 'interest_mortgage',
            'labor', 'pension', 'rent_lease', 'repairs', 'seeds',
            'storage', 'supplies', 'taxes', 'utilities', 'veterinary',
            'other_expenses'
        ]
        
        for category in expense_categories:
            if category in data:
                elem = ElementTree.SubElement(parent, category.title())
                elem.text = str(data[category])
        
        total = ElementTree.SubElement(parent, 'TotalExpenses')
        total.text = str(self._calculate_total_expenses(data))

    def _add_depreciation_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add depreciation information"""
        assets = data.get('assets', [])
        
        for asset in assets:
            asset_elem = ElementTree.SubElement(parent, 'DepreciableAsset')
            
            description = ElementTree.SubElement(asset_elem, 'Description')
            description.text = asset.get('description', '')
            
            cost = ElementTree.SubElement(asset_elem, 'Cost')
            cost.text = str(asset.get('cost', '0'))
            
            date_placed = ElementTree.SubElement(asset_elem, 'DatePlaced')
            date_placed.text = asset.get('date_placed', '')
            
            method = ElementTree.SubElement(asset_elem, 'Method')
            method.text = asset.get('method', '')
            
            life = ElementTree.SubElement(asset_elem, 'Life')
            life.text = str(asset.get('life', '0'))
            
            amount = ElementTree.SubElement(asset_elem, 'Amount')
            amount.text = str(asset.get('amount', '0'))

    def _calculate_total_income(self, data: Dict[str, Any]) -> Decimal:
        """Calculate total farm income"""
        return sum(Decimal(str(amount)) for amount in data.values())

    def _calculate_total_expenses(self, data: Dict[str, Any]) -> Decimal:
        """Calculate total farm expenses"""
        return sum(Decimal(str(amount)) for amount in data.values())
