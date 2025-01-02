from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form4684Template(BaseMeFTemplate):
    """Template for Form 4684 (Casualties and Thefts)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form4684"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 4684 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 4684
        form = ElementTree.SubElement(root, "Form4684")

        # Add Section A - Personal Use Property
        section_a = ElementTree.SubElement(form, "SectionA")
        self._add_section_a(section_a, data.get("section_a", {}))

        # Add Section B - Business and Income-Producing Property
        section_b = ElementTree.SubElement(form, "SectionB")
        self._add_section_b(section_b, data.get("section_b", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "4684_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_section_a(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Section A - Personal Use Property"""
        for property_data in data.get("properties", []):
            property_entry = ElementTree.SubElement(parent, "Property")
            
            description = ElementTree.SubElement(property_entry, "Description")
            description.text = property_data.get("description", "")

            date_acquired = ElementTree.SubElement(property_entry, "DateAcquired")
            date_acquired.text = property_data.get("date_acquired", "")

            date_damaged = ElementTree.SubElement(property_entry, "DateDamaged")
            date_damaged.text = property_data.get("date_damaged", "")

            cost = ElementTree.SubElement(property_entry, "Cost")
            cost.text = str(property_data.get("cost", "0.00"))

            fair_market_value_before = ElementTree.SubElement(property_entry, "FairMarketValueBefore")
            fair_market_value_before.text = str(property_data.get("fmv_before", "0.00"))

            fair_market_value_after = ElementTree.SubElement(property_entry, "FairMarketValueAfter")
            fair_market_value_after.text = str(property_data.get("fmv_after", "0.00"))

            insurance = ElementTree.SubElement(property_entry, "Insurance")
            insurance.text = str(property_data.get("insurance", "0.00"))

    def _add_section_b(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Section B - Business and Income-Producing Property"""
        for property_data in data.get("properties", []):
            property_entry = ElementTree.SubElement(parent, "Property")
            
            description = ElementTree.SubElement(property_entry, "Description")
            description.text = property_data.get("description", "")

            business_type = ElementTree.SubElement(property_entry, "BusinessType")
            business_type.text = property_data.get("business_type", "")

            date_acquired = ElementTree.SubElement(property_entry, "DateAcquired")
            date_acquired.text = property_data.get("date_acquired", "")

            date_damaged = ElementTree.SubElement(property_entry, "DateDamaged")
            date_damaged.text = property_data.get("date_damaged", "")

            cost_basis = ElementTree.SubElement(property_entry, "CostBasis")
            cost_basis.text = str(property_data.get("cost_basis", "0.00"))

            insurance = ElementTree.SubElement(property_entry, "Insurance")
            insurance.text = str(property_data.get("insurance", "0.00"))

            depreciation = ElementTree.SubElement(property_entry, "Depreciation")
            depreciation.text = str(property_data.get("depreciation", "0.00"))
