from typing import Dict, Any, List
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate


class Form8938Template(BaseMeFTemplate):
    """Template for Form 8938 (Statement of Specified Foreign Financial Assets)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form8938"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 8938 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add enhanced foreign asset reporting
        form = ElementTree.SubElement(root, "Form8938")

        # Add detailed asset reporting
        assets = ElementTree.SubElement(form, "ForeignAssets")
        self._add_foreign_assets(assets, data.get("assets", []))

        # Add summary information
        summary = ElementTree.SubElement(form, "Summary")
        self._add_summary(summary, data.get("summary", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "8938_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_foreign_assets(
        self, parent: ElementTree.Element, assets: List[Dict[str, Any]]
    ) -> None:
        """Add foreign assets section"""
        for asset in assets:
            # Enhanced asset validation
            if not self._validate_asset_data(asset):
                raise ValueError(f"Invalid asset data: {asset}")

            asset_elem = ElementTree.SubElement(parent, "ForeignAsset")

            # Add detailed asset information
            self._add_asset_info(asset_elem, asset)

            # Add asset type classification
            asset_type = ElementTree.SubElement(asset_elem, "AssetType")
            asset_type.text = self._classify_asset_type(asset)

    def _add_asset_info(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add detailed asset information"""
        # Asset description
        description = ElementTree.SubElement(parent, "Description")
        description.text = data.get("description", "")

        # Asset value
        value = ElementTree.SubElement(parent, "Value")
        value.text = str(data.get("value", "0.00"))

        # Asset location
        location = ElementTree.SubElement(parent, "Location")
        self._add_address(location, data.get("location", {}))

        # Acquisition information
        acquisition = ElementTree.SubElement(parent, "Acquisition")
        self._add_acquisition_info(acquisition, data.get("acquisition", {}))

    def _add_acquisition_info(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add asset acquisition information"""
        date = ElementTree.SubElement(parent, "Date")
        date.text = data.get("date", "")

        cost = ElementTree.SubElement(parent, "Cost")
        cost.text = str(data.get("cost", "0.00"))

        method = ElementTree.SubElement(parent, "Method")
        method.text = data.get("method", "")

    def _add_summary(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add summary information"""
        total_accounts = ElementTree.SubElement(parent, "TotalForeignAccounts")
        total_accounts.text = str(data.get("total_accounts", "0"))

        total_assets = ElementTree.SubElement(parent, "TotalForeignAssets")
        total_assets.text = str(data.get("total_assets", "0"))

        total_value = ElementTree.SubElement(parent, "TotalValue")
        total_value.text = str(data.get("total_value", "0.00"))

    def _validate_asset_data(self, asset: Dict[str, Any]) -> bool:
        """Validate asset data"""
        # Implement validation logic here
        return True

    def _classify_asset_type(self, asset: Dict[str, Any]) -> str:
        """Classify asset type"""
        # Implement classification logic here
        return "Unknown"
