from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form8949Template(BaseMeFTemplate):
    """Template for Form 8949 (Sales and Other Dispositions of Capital Assets)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form8949"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 8949 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 8949
        form = ElementTree.SubElement(root, "Form8949")

        # Add Short-term transactions
        short_term = ElementTree.SubElement(form, "ShortTerm")
        self._add_transactions(short_term, data.get("short_term", {}))

        # Add Long-term transactions
        long_term = ElementTree.SubElement(form, "LongTerm")
        self._add_transactions(long_term, data.get("long_term", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "8949_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_transactions(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add transaction information"""
        for transaction in data.get("transactions", []):
            trans_element = ElementTree.SubElement(parent, "Transaction")
            
            description = ElementTree.SubElement(trans_element, "Description")
            description.text = transaction.get("description", "")

            date_acquired = ElementTree.SubElement(trans_element, "DateAcquired")
            date_acquired.text = transaction.get("date_acquired", "")

            date_sold = ElementTree.SubElement(trans_element, "DateSold")
            date_sold.text = transaction.get("date_sold", "")

            proceeds = ElementTree.SubElement(trans_element, "Proceeds")
            proceeds.text = str(transaction.get("proceeds", "0.00"))

            cost_basis = ElementTree.SubElement(trans_element, "CostBasis")
            cost_basis.text = str(transaction.get("cost_basis", "0.00"))

            adjustment = ElementTree.SubElement(trans_element, "Adjustment")
            adjustment.text = str(transaction.get("adjustment", "0.00"))

            gain_loss = ElementTree.SubElement(trans_element, "GainLoss")
            gain_loss.text = str(transaction.get("gain_loss", "0.00"))

            self._add_codes(trans_element, transaction.get("codes", {}))

    def _add_codes(self, parent: ElementTree.Element, codes: Dict[str, Any]) -> None:
        """Add transaction codes"""
        if codes.get("basis_reported"):
            code = ElementTree.SubElement(parent, "BasisReported")
            code.text = "true"

        if codes.get("wash_sale"):
            code = ElementTree.SubElement(parent, "WashSale")
            code.text = "true"

        if codes.get("federal_excluded"):
            code = ElementTree.SubElement(parent, "FederalExcluded")
            code.text = "true"
