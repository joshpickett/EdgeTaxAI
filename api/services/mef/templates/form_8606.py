from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form8606Template(BaseMeFTemplate):
    """Template for Form 8606 (Nondeductible IRAs)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form8606"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 8606 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 8606
        form = ElementTree.SubElement(root, "Form8606")

        # Add Traditional IRA information
        traditional_ira = ElementTree.SubElement(form, "TraditionalIRA")
        self._add_traditional_ira(traditional_ira, data.get("traditional_ira", {}))

        # Add Roth IRA conversion information
        roth_conversion = ElementTree.SubElement(form, "RothConversion")
        self._add_roth_conversion(roth_conversion, data.get("roth_conversion", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "8606_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_traditional_ira(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Traditional IRA information"""
        nondeductible_contributions = ElementTree.SubElement(parent, "NondeductibleContributions")
        nondeductible_contributions.text = str(data.get("nondeductible_contributions", "0.00"))

        basis = ElementTree.SubElement(parent, "Basis")
        basis.text = str(data.get("basis", "0.00"))

        distributions = ElementTree.SubElement(parent, "Distributions")
        distributions.text = str(data.get("distributions", "0.00"))

        nontaxable_amount = ElementTree.SubElement(parent, "NontaxableAmount")
        nontaxable_amount.text = str(data.get("nontaxable_amount", "0.00"))

        taxable_amount = ElementTree.SubElement(parent, "TaxableAmount")
        taxable_amount.text = str(data.get("taxable_amount", "0.00"))

    def _add_roth_conversion(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Roth IRA conversion information"""
        conversion_amount = ElementTree.SubElement(parent, "ConversionAmount")
        conversion_amount.text = str(data.get("conversion_amount", "0.00"))

        taxable_amount = ElementTree.SubElement(parent, "TaxableAmount")
        taxable_amount.text = str(data.get("taxable_amount", "0.00"))

        nontaxable_amount = ElementTree.SubElement(parent, "NontaxableAmount")
        nontaxable_amount.text = str(data.get("nontaxable_amount", "0.00"))

        basis_remaining = ElementTree.SubElement(parent, "BasisRemaining")
        basis_remaining.text = str(data.get("basis_remaining", "0.00"))
