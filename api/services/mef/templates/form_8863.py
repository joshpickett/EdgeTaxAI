from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form8863Template(BaseMeFTemplate):
    """Template for Form 8863 (Education Credits)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form8863"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 8863 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 8863
        form = ElementTree.SubElement(root, "Form8863")

        # Add American Opportunity Credit
        american_opportunity_credit = ElementTree.SubElement(form, "AmericanOpportunityCredit")
        self._add_american_opportunity_credit(american_opportunity_credit, data.get("american_opportunity", {}))

        # Add Lifetime Learning Credit
        lifetime_learning_credit = ElementTree.SubElement(form, "LifetimeLearningCredit")
        self._add_lifetime_learning_credit(lifetime_learning_credit, data.get("lifetime_learning", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "8863_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_american_opportunity_credit(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add American Opportunity Credit information"""
        for student in data.get("students", []):
            student_element = ElementTree.SubElement(parent, "Student")
            
            name = ElementTree.SubElement(student_element, "Name")
            name.text = student.get("name", "")

            social_security_number = ElementTree.SubElement(student_element, "SocialSecurityNumber")
            social_security_number.text = student.get("ssn", "")

            institution = ElementTree.SubElement(student_element, "Institution")
            self._add_institution_info(institution, student.get("institution", {}))

            qualified_expenses = ElementTree.SubElement(student_element, "QualifiedExpenses")
            qualified_expenses.text = str(student.get("qualified_expenses", "0.00"))

            credit_amount = ElementTree.SubElement(student_element, "CreditAmount")
            credit_amount.text = str(student.get("credit_amount", "0.00"))

    def _add_lifetime_learning_credit(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Lifetime Learning Credit information"""
        for student in data.get("students", []):
            student_element = ElementTree.SubElement(parent, "Student")
            
            name = ElementTree.SubElement(student_element, "Name")
            name.text = student.get("name", "")

            social_security_number = ElementTree.SubElement(student_element, "SocialSecurityNumber")
            social_security_number.text = student.get("ssn", "")

            institution = ElementTree.SubElement(student_element, "Institution")
            self._add_institution_info(institution, student.get("institution", {}))

            qualified_expenses = ElementTree.SubElement(student_element, "QualifiedExpenses")
            qualified_expenses.text = str(student.get("qualified_expenses", "0.00"))

            credit_amount = ElementTree.SubElement(student_element, "CreditAmount")
            credit_amount.text = str(student.get("credit_amount", "0.00"))

    def _add_institution_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add educational institution information"""
        name = ElementTree.SubElement(parent, "Name")
        name.text = data.get("name", "")

        employer_identification_number = ElementTree.SubElement(parent, "EmployerIdentificationNumber")
        employer_identification_number.text = data.get("ein", "")

        address = ElementTree.SubElement(parent, "Address")
        self._add_address(address, data.get("address", {}))
