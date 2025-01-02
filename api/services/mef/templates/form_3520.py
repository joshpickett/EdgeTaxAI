from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form3520Template(BaseMeFTemplate):
    """Template for Form 3520 (Foreign Gifts and Trusts)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form3520"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 3520 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 3520
        form = ElementTree.SubElement(root, "Form3520")

        # Add foreign gift information
        gifts = ElementTree.SubElement(form, "ForeignGifts")
        self._add_foreign_gifts(gifts, data.get("gifts", []))

        # Add foreign trust information
        trusts = ElementTree.SubElement(form, "ForeignTrusts")
        self._add_foreign_trusts(trusts, data.get("trusts", []))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "3520_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_foreign_gifts(self, parent: ElementTree.Element, gifts: list) -> None:
        """Add foreign gift information"""
        for gift in gifts:
            gift_element = ElementTree.SubElement(parent, "ForeignGift")
            
            donor = ElementTree.SubElement(gift_element, "Donor")
            self._add_foreign_person(donor, gift.get("donor", {}))

            date = ElementTree.SubElement(gift_element, "DateReceived")
            date.text = gift.get("date_received", "")

            description = ElementTree.SubElement(gift_element, "Description")
            description.text = gift.get("description", "")

            value = ElementTree.SubElement(gift_element, "FairMarketValue")
            value.text = str(gift.get("fair_market_value", "0.00"))

    def _add_foreign_trusts(self, parent: ElementTree.Element, trusts: list) -> None:
        """Add foreign trust information"""
        for trust in trusts:
            trust_element = ElementTree.SubElement(parent, "ForeignTrust")
            
            name = ElementTree.SubElement(trust_element, "TrustName")
            name.text = trust.get("name", "")

            country = ElementTree.SubElement(trust_element, "Country")
            country.text = trust.get("country", "")

            tin = ElementTree.SubElement(trust_element, "ForeignTIN")
            tin.text = trust.get("foreign_tin", "")

            transfers = ElementTree.SubElement(trust_element, "Transfers")
            self._add_trust_transfers(transfers, trust.get("transfers", []))

    def _add_foreign_person(self, parent: ElementTree.Element, person: Dict[str, Any]) -> None:
        """Add foreign person information"""
        name = ElementTree.SubElement(parent, "Name")
        name.text = person.get("name", "")

        address = ElementTree.SubElement(parent, "Address")
        self._add_address(address, person.get("address", {}))

        country = ElementTree.SubElement(parent, "Country")
        country.text = person.get("country", "")

        tin = ElementTree.SubElement(parent, "ForeignTIN")
        tin.text = person.get("foreign_tin", "")

    def _add_trust_transfers(self, parent: ElementTree.Element, transfers: list) -> None:
        """Add trust transfer information"""
        for transfer in transfers:
            transfer_element = ElementTree.SubElement(parent, "Transfer")
            
            type_code = ElementTree.SubElement(transfer_element, "TypeCode")
            type_code.text = transfer.get("type_code", "")

            date = ElementTree.SubElement(transfer_element, "Date")
            date.text = transfer.get("date", "")

            description = ElementTree.SubElement(transfer_element, "Description")
            description.text = transfer.get("description", "")

            value = ElementTree.SubElement(transfer_element, "Value")
            value.text = str(transfer.get("value", "0.00"))

    def _add_address(self, parent: ElementTree.Element, address: Dict[str, Any]) -> None:
        """Add address information"""
        street = ElementTree.SubElement(parent, "Street")
        street.text = address.get("street", "")

        city = ElementTree.SubElement(parent, "City")
        city.text = address.get("city", "")

        province = ElementTree.SubElement(parent, "Province")
        province.text = address.get("province", "")

        postal_code = ElementTree.SubElement(parent, "PostalCode")
        postal_code.text = address.get("postal_code", "")

        country = ElementTree.SubElement(parent, "Country")
        country.text = address.get("country", "")
