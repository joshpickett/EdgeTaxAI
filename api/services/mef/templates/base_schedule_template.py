from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate


class BaseScheduleTemplate(BaseMeFTemplate):
    """Base template for Schedule forms"""

    def __init__(self):
        super().__init__()
        self.schedule_type = None

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Schedule XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Schedule
        schedule = ElementTree.SubElement(root, f"Schedule{self.schedule_type}")

        # Add TaxPayer Information
        taxpayer_info = ElementTree.SubElement(schedule, "TaxpayerInfo")
        self._add_taxpayer_info(taxpayer_info, data)

        # Add Schedule-specific content
        self._add_schedule_content(schedule, data)

        xml_string = self.prettify_xml(root)

        # Validate against schema
        schema_file = f"schedule_{self.schedule_type.lower()}_2023v1.0.xsd"
        if not self.validate_xml(xml_string, schema_file):
            raise ValueError(
                f"Generated Schedule {self.schedule_type} XML failed schema validation"
            )

        return xml_string

    def _add_schedule_content(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add schedule-specific content - to be implemented by child classes"""
        raise NotImplementedError(
            "Schedule content must be implemented by child classes"
        )

    def _add_taxpayer_info(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add taxpayer information"""
        taxpayer_data = data.get("taxpayer", {})

        name = ElementTree.SubElement(parent, "Name")
        name.text = taxpayer_data.get("name", "")

        ssn = ElementTree.SubElement(parent, "SSN")
        ssn.text = taxpayer_data.get("ssn", "")
