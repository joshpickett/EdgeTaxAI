from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form4562Template(BaseMeFTemplate):
    """Template for Form 4562 (Depreciation and Amortization)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form4562"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 4562 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 4562
        form = ElementTree.SubElement(root, "Form4562")

        # Add Section 179 expense
        section_179 = ElementTree.SubElement(form, "Section179")
        self._add_section_179(section_179, data.get("section_179", {}))

        # Add Special depreciation allowance
        special_allowance = ElementTree.SubElement(form, "SpecialAllowance")
        self._add_special_allowance(special_allowance, data.get("special_allowance", {}))

        # Add Modified Accelerated Cost Recovery System depreciation
        macrs = ElementTree.SubElement(form, "MACRS")
        self._add_macrs_depreciation(macrs, data.get("macrs", {}))

        # Add Listed property
        listed_property = ElementTree.SubElement(form, "ListedProperty")
        self._add_listed_property(listed_property, data.get("listed_property", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "4562_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_section_179(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Section 179 expense information"""
        total_cost = ElementTree.SubElement(parent, "TotalCost")
        total_cost.text = str(data.get("total_cost", "0.00"))

        threshold = ElementTree.SubElement(parent, "Threshold")
        threshold.text = str(data.get("threshold", "0.00"))

        reduction = ElementTree.SubElement(parent, "Reduction")
        reduction.text = str(data.get("reduction", "0.00"))

        elected_cost = ElementTree.SubElement(parent, "ElectedCost")
        elected_cost.text = str(data.get("elected_cost", "0.00"))

    def _add_special_allowance(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add special depreciation allowance information"""
        qualified_property = ElementTree.SubElement(parent, "QualifiedProperty")
        qualified_property.text = str(data.get("qualified_property", "0.00"))

        listed_property = ElementTree.SubElement(parent, "ListedProperty")
        listed_property.text = str(data.get("listed_property", "0.00"))

        qualified_improvement = ElementTree.SubElement(parent, "QualifiedImprovement")
        qualified_improvement.text = str(data.get("qualified_improvement", "0.00"))

    def _add_macrs_depreciation(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Modified Accelerated Cost Recovery System depreciation information"""
        # Add General Depreciation System
        gds = ElementTree.SubElement(parent, "GDS")
        self._add_depreciation_class(gds, data.get("gds", {}))

        # Add Alternative Depreciation System
        ads = ElementTree.SubElement(parent, "ADS")
        self._add_depreciation_class(ads, data.get("ads", {}))

    def _add_depreciation_class(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add depreciation class information"""
        for year, year_data in data.items():
            class_entry = ElementTree.SubElement(parent, "DepreciationClass")
            
            recovery_period = ElementTree.SubElement(class_entry, "RecoveryPeriod")
            recovery_period.text = year

            basis = ElementTree.SubElement(class_entry, "Basis")
            basis.text = str(year_data.get("basis", "0.00"))

            convention = ElementTree.SubElement(class_entry, "Convention")
            convention.text = year_data.get("convention", "")

            method = ElementTree.SubElement(class_entry, "Method")
            method.text = year_data.get("method", "")

            depreciation = ElementTree.SubElement(class_entry, "Depreciation")
            depreciation.text = str(year_data.get("depreciation", "0.00"))

    def _add_listed_property(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add listed property information"""
        for property_data in data.get("properties", []):
            property_entry = ElementTree.SubElement(parent, "Property")
            
            type_code = ElementTree.SubElement(property_entry, "TypeCode")
            type_code.text = property_data.get("type_code", "")

            date_placed = ElementTree.SubElement(property_entry, "DatePlaced")
            date_placed.text = property_data.get("date_placed", "")

            business_use = ElementTree.SubElement(property_entry, "BusinessUse")
            business_use.text = str(property_data.get("business_use", "0.00"))

            cost = ElementTree.SubElement(property_entry, "Cost")
            cost.text = str(property_data.get("cost", "0.00"))
