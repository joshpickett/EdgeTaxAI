from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate


class Form8829Template(BaseMeFTemplate):
    """Template for Form 8829 (Home Office) XML generation"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form8829"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 8829 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form8829
        form = ElementTree.SubElement(root, "Form8829")

        # Add taxpayer information
        taxpayer = ElementTree.SubElement(form, "TaxpayerInfo")
        self._add_taxpayer_info(taxpayer, data.get("taxpayer", {}))

        # Add home office information
        home_office = ElementTree.SubElement(form, "HomeOfficeInfo")
        self._add_home_office_info(home_office, data.get("home_office", {}))

        # Add expense information
        expenses = ElementTree.SubElement(form, "Expenses")
        self._add_expenses(expenses, data.get("expenses", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "8829_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_home_office_info(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add home office information"""
        total_area = ElementTree.SubElement(parent, "TotalHomeArea")
        total_area.text = str(data.get("total_area", "0"))

        office_area = ElementTree.SubElement(parent, "OfficeArea")
        office_area.text = str(data.get("office_area", "0"))

        percentage = ElementTree.SubElement(parent, "BusinessPercentage")
        percentage.text = str(
            self._calculate_percentage(
                data.get("office_area", 0), data.get("total_area", 1)
            )
        )

    def _add_expenses(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add expense information"""
        # Direct expenses
        direct = ElementTree.SubElement(parent, "DirectExpenses")
        self._add_expense_category(direct, data.get("direct", {}))

        # Indirect expenses
        indirect = ElementTree.SubElement(parent, "IndirectExpenses")
        self._add_expense_category(indirect, data.get("indirect", {}))

        # Depreciation
        depreciation = ElementTree.SubElement(parent, "Depreciation")
        self._add_depreciation_info(depreciation, data.get("depreciation", {}))

    def _add_expense_category(
        self, parent: ElementTree.Element, expenses: Dict[str, Any]
    ) -> None:
        """Add expense category details"""
        categories = [
            "repairs",
            "utilities",
            "insurance",
            "maintenance",
            "mortgage_interest",
            "property_taxes",
            "other",
        ]

        for category in categories:
            if category in expenses:
                elem = ElementTree.SubElement(parent, category.title())
                elem.text = str(expenses[category])

    def _add_depreciation_info(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add depreciation information"""
        basis = ElementTree.SubElement(parent, "DepreciableBasis")
        basis.text = str(data.get("basis", "0"))

        rate = ElementTree.SubElement(parent, "DepreciationRate")
        rate.text = str(data.get("rate", "0"))

        amount = ElementTree.SubElement(parent, "DepreciationAmount")
        amount.text = str(data.get("amount", "0"))

    def _calculate_percentage(self, office_area: float, total_area: float) -> float:
        """Calculate business use percentage"""
        if not total_area:
            return 0
        return round((office_area / total_area) * 100, 2)
