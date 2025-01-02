from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate


class Form2555Template(BaseMeFTemplate):
    """Template for Form 2555 (Foreign Earned Income) XML generation"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form2555"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 2555 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 2555 with enhanced foreign income exclusion
        form = ElementTree.SubElement(root, "Form2555")

        # Add taxpayer information
        taxpayer = ElementTree.SubElement(form, "TaxpayerInfo")
        self._add_taxpayer_info(taxpayer, data.get("taxpayer", {}))

        # Add foreign address and employer information
        foreign_address = ElementTree.SubElement(form, "ForeignAddress")
        self._add_foreign_address(foreign_address, data.get("foreign_address", {}))

        # Add employer information with enhanced validation
        employer = ElementTree.SubElement(form, "EmployerInfo")
        self._add_employer_info(employer, data.get("employer", {}))

        # Add detailed foreign income breakdown
        income_types = [
            ("salary", "Salary"),
            ("bonus", "Bonus"),
            ("allowances", "Allowances"),
            ("other_income", "OtherIncome"),
        ]

        for income_type, tag in income_types:
            element = ElementTree.SubElement(form, tag)
            element.text = str(data.get(income_type, "0.00"))

        # Add income exclusion calculation
        exclusion = ElementTree.SubElement(form, "ForeignEarnedIncomeExclusion")
        exclusion.text = str(self._calculate_exclusion(data))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "2555_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_foreign_address(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add foreign address information"""
        street = ElementTree.SubElement(parent, "Street")
        street.text = data.get("street", "")

        city = ElementTree.SubElement(parent, "City")
        city.text = data.get("city", "")

        province = ElementTree.SubElement(parent, "Province")
        province.text = data.get("province", "")

        country = ElementTree.SubElement(parent, "Country")
        country.text = data.get("country", "")

        postal_code = ElementTree.SubElement(parent, "PostalCode")
        postal_code.text = data.get("postal_code", "")

    def _add_employer_info(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add employer information"""
        name = ElementTree.SubElement(parent, "EmployerName")
        name.text = data.get("name", "")

        employer_type = ElementTree.SubElement(parent, "EmployerType")
        employer_type.text = data.get("type", "")

        address = ElementTree.SubElement(parent, "EmployerAddress")
        self._add_foreign_address(address, data.get("address", {}))

    def _add_foreign_income(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add foreign earned income information"""
        # Add detailed foreign income breakdown
        income_types = [
            ("salary", "Salary"),
            ("bonus", "Bonus"),
            ("allowances", "Allowances"),
            ("other_income", "OtherIncome"),
        ]

        for income_type, tag in income_types:
            element = ElementTree.SubElement(parent, tag)
            element.text = str(data.get(income_type, "0.00"))

        # Add income exclusion calculation
        exclusion = ElementTree.SubElement(parent, "ForeignEarnedIncomeExclusion")
        exclusion.text = str(self._calculate_exclusion(data))

    def _add_housing_exclusion(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add housing exclusion information"""
        housing_expenses = ElementTree.SubElement(parent, "HousingExpenses")
        housing_expenses.text = str(data.get("expenses", "0.00"))

        base_amount = ElementTree.SubElement(parent, "BaseAmount")
        base_amount.text = str(data.get("base_amount", "0.00"))

        housing_exclusion = ElementTree.SubElement(parent, "HousingExclusionAmount")
        housing_exclusion.text = str(data.get("exclusion_amount", "0.00"))
