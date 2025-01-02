from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form8283Template(BaseMeFTemplate):
    """Template for Form 8283 (Noncash Charitable Contributions)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form8283"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 8283 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 8283
        form = ElementTree.SubElement(root, "Form8283")

        # Add Section A - Donated Property $5,000 or Less
        section_a = ElementTree.SubElement(form, "SectionA")
        self._add_section_a(section_a, data.get("section_a", {}))

        # Add Section B - Donated Property Over $5,000
        section_b = ElementTree.SubElement(form, "SectionB")
        self._add_section_b(section_b, data.get("section_b", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "8283_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_section_a(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Section A - Donated Property $5,000 or Less"""
        for donation in data.get("donations", []):
            donation_element = ElementTree.SubElement(parent, "Donation")
            
            organization = ElementTree.SubElement(donation_element, "Organization")
            self._add_organization_info(organization, donation.get("organization", {}))

            property_info = ElementTree.SubElement(donation_element, "PropertyInfo")
            self._add_property_info(property_info, donation.get("property", {}))

            valuation = ElementTree.SubElement(donation_element, "Valuation")
            self._add_valuation_info(valuation, donation.get("valuation", {}))

    def _add_section_b(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Section B - Donated Property Over $5,000"""
        for donation in data.get("donations", []):
            donation_element = ElementTree.SubElement(parent, "Donation")
            
            organization = ElementTree.SubElement(donation_element, "Organization")
            self._add_organization_info(organization, donation.get("organization", {}))

            property_info = ElementTree.SubElement(donation_element, "PropertyInfo")
            self._add_property_info(property_info, donation.get("property", {}))

            appraisal = ElementTree.SubElement(donation_element, "Appraisal")
            self._add_appraisal_info(appraisal, donation.get("appraisal", {}))

            declaration = ElementTree.SubElement(donation_element, "Declaration")
            self._add_declaration_info(declaration, donation.get("declaration", {}))

    def _add_organization_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add organization information"""
        name = ElementTree.SubElement(parent, "Name")
        name.text = data.get("name", "")

        ein = ElementTree.SubElement(parent, "EIN")
        ein.text = data.get("ein", "")

        address = ElementTree.SubElement(parent, "Address")
        self._add_address(address, data.get("address", {}))

    def _add_property_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add property information"""
        description = ElementTree.SubElement(parent, "Description")
        description.text = data.get("description", "")

        acquisition_date = ElementTree.SubElement(parent, "AcquisitionDate")
        acquisition_date.text = data.get("acquisition_date", "")

        how_acquired = ElementTree.SubElement(parent, "HowAcquired")
        how_acquired.text = data.get("how_acquired", "")

        cost_basis = ElementTree.SubElement(parent, "CostBasis")
        cost_basis.text = str(data.get("cost_basis", "0.00"))

    def _add_valuation_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add valuation information"""
        fair_market_value = ElementTree.SubElement(parent, "FairMarketValue")
        fair_market_value.text = str(data.get("fair_market_value", "0.00"))

        valuation_method = ElementTree.SubElement(parent, "ValuationMethod")
        valuation_method.text = data.get("valuation_method", "")

    def _add_appraisal_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add appraisal information"""
        appraiser_name = ElementTree.SubElement(parent, "AppraiserName")
        appraiser_name.text = data.get("appraiser_name", "")

        appraiser_tax_id = ElementTree.SubElement(parent, "AppraiserTaxID")
        appraiser_tax_id.text = data.get("appraiser_tax_id", "")

        appraisal_date = ElementTree.SubElement(parent, "AppraisalDate")
        appraisal_date.text = data.get("appraisal_date", "")

        appraised_value = ElementTree.SubElement(parent, "AppraisedValue")
        appraised_value.text = str(data.get("appraised_value", "0.00"))

    def _add_declaration_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add declaration information"""
        signature_date = ElementTree.SubElement(parent, "SignatureDate")
        signature_date.text = data.get("signature_date", "")

        title = ElementTree.SubElement(parent, "Title")
        title.text = data.get("title", "")
