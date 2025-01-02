from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form2441Template(BaseMeFTemplate):
    """Template for Form 2441 (Child and Dependent Care Expenses)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form2441"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 2441 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 2441
        form = ElementTree.SubElement(root, "Form2441")

        # Add care provider information
        providers = ElementTree.SubElement(form, "CareProviders")
        self._add_care_providers(providers, data.get("providers", []))

        # Add qualifying person information
        qualifying_persons = ElementTree.SubElement(form, "QualifyingPersons")
        self._add_qualifying_persons(qualifying_persons, data.get("qualifying_persons", []))

        # Add expense calculations
        expenses = ElementTree.SubElement(form, "ExpenseCalculations")
        self._add_expense_calculations(expenses, data)

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "2441_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_care_providers(self, parent: ElementTree.Element, providers: list) -> None:
        """Add care provider information"""
        for provider in providers:
            provider_element = ElementTree.SubElement(parent, "CareProvider")
            
            name = ElementTree.SubElement(provider_element, "Name")
            name.text = provider.get("name", "")

            tax_id = ElementTree.SubElement(provider_element, "TaxID")
            tax_id.text = provider.get("tax_id", "")

            address = ElementTree.SubElement(provider_element, "Address")
            self._add_address(address, provider.get("address", {}))

            amount = ElementTree.SubElement(provider_element, "AmountPaid")
            amount.text = str(provider.get("amount_paid", "0.00"))

    def _add_qualifying_persons(self, parent: ElementTree.Element, persons: list) -> None:
        """Add qualifying person information"""
        for person in persons:
            person_element = ElementTree.SubElement(parent, "QualifyingPerson")
            
            name = ElementTree.SubElement(person_element, "Name")
            name.text = person.get("name", "")

            social_security_number = ElementTree.SubElement(person_element, "SocialSecurityNumber")
            social_security_number.text = person.get("ssn", "")

            relationship = ElementTree.SubElement(person_element, "Relationship")
            relationship.text = person.get("relationship", "")

            qualified_expenses = ElementTree.SubElement(person_element, "QualifiedExpenses")
            qualified_expenses.text = str(person.get("qualified_expenses", "0.00"))

    def _add_expense_calculations(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add expense calculations"""
        total_expenses = ElementTree.SubElement(parent, "TotalExpenses")
        total_expenses.text = str(data.get("total_expenses", "0.00"))

        earned_income = ElementTree.SubElement(parent, "EarnedIncome")
        earned_income.text = str(data.get("earned_income", "0.00"))

        credit_limit = ElementTree.SubElement(parent, "CreditLimit")
        credit_limit.text = str(data.get("credit_limit", "0.00"))

        credit_amount = ElementTree.SubElement(parent, "CreditAmount")
        credit_amount.text = str(data.get("credit_amount", "0.00"))

    def _add_address(self, parent: ElementTree.Element, address: Dict[str, Any]) -> None:
        """Add address information"""
        street = ElementTree.SubElement(parent, "Street")
        street.text = address.get("street", "")

        city = ElementTree.SubElement(parent, "City")
        city.text = address.get("city", "")

        state = ElementTree.SubElement(parent, "State")
        state.text = address.get("state", "")

        zip_code = ElementTree.SubElement(parent, "ZipCode")
        zip_code.text = address.get("zip_code", "")
