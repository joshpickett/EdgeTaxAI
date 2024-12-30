from typing import Dict, Any, List
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_schedule_template import BaseScheduleTemplate

class ScheduleETemplate(BaseScheduleTemplate):
    """Template for Schedule E (Rental Income) XML generation"""
    
    def __init__(self):
        super().__init__()
        self.schedule_type = 'E'

    def _add_schedule_content(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Schedule E specific content"""
        properties = data.get('properties', [])
        
        # Add rental properties
        rental_properties = ElementTree.SubElement(parent, 'RentalProperties')
        for property_data in properties:
            self._add_property(rental_properties, property_data)
            
        # Add totals
        totals = ElementTree.SubElement(parent, 'Totals')
        self._add_totals(totals, self._calculate_totals(properties))

    def _add_property(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add individual property information"""
        property_element = ElementTree.SubElement(parent, 'Property')
        
        # Property information
        address = ElementTree.SubElement(property_element, 'PropertyAddress')
        self._add_address(address, data.get('address', {}))
        
        # Property type
        property_type = ElementTree.SubElement(property_element, 'PropertyType')
        property_type.text = data.get('type', '')
        
        # Income information
        income = ElementTree.SubElement(property_element, 'Income')
        self._add_income_info(income, data.get('income', {}))
        
        # Expenses information
        expenses = ElementTree.SubElement(property_element, 'Expenses')
        self._add_expense_info(expenses, data.get('expenses', {}))

    def _add_income_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add income information"""
        rents = ElementTree.SubElement(parent, 'RentsReceived')
        rents.text = str(data.get('rents', '0'))
        
        other = ElementTree.SubElement(parent, 'OtherIncome')
        other.text = str(data.get('other', '0'))

    def _add_expense_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add expense information"""
        expense_categories = [
            'advertising', 'auto_travel', 'cleaning', 'commissions',
            'insurance', 'legal', 'management_fees', 'mortgage_interest',
            'repairs', 'supplies', 'taxes', 'utilities'
        ]
        
        for category in expense_categories:
            if category in data:
                element = ElementTree.SubElement(parent, category.title())
                element.text = str(data[category])

    def _calculate_totals(self, properties: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """Calculate totals across all properties"""
        totals = {
            'total_income': Decimal('0'),
            'total_expenses': Decimal('0'),
            'net_income': Decimal('0')
        }
        
        for property_data in properties:
            income = property_data.get('income', {})
            expenses = property_data.get('expenses', {})
            
            total_income = Decimal(str(income.get('rents', 0))) + \
                          Decimal(str(income.get('other', 0)))
            total_expenses = sum(Decimal(str(amount)) for amount in expenses.values())
            
            totals['total_income'] += total_income
            totals['total_expenses'] += total_expenses
            
        totals['net_income'] = totals['total_income'] - totals['total_expenses']
        return totals

    def _add_totals(self, parent: ElementTree.Element, totals: Dict[str, Decimal]) -> None:
        """Add totals section"""
        for key, value in totals.items():
            element = ElementTree.SubElement(parent, key.title())
            element.text = str(value)
