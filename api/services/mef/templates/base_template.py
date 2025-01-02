from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from lxml import etree
import logging
from api.config.mef_config import MEF_CONFIG


class BaseMeFTemplate:
    """Base class for MeF XML templates"""

    def __init__(self):
        self.namespaces = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "irs": "http://www.irs.gov/efile",
        }
        self.schema_path = MEF_CONFIG["VALIDATION"]["SCHEMA_PATH"]
        self.logger = logging.getLogger(__name__)

    def create_base_xml(self) -> ElementTree.Element:
        """Create base XML structure for MeF submission"""
        ElementTree.register_namespace("xsi", self.namespaces["xsi"])
        ElementTree.register_namespace("irs", self.namespaces["irs"])

        root = ElementTree.Element("{%s}Return" % self.namespaces["irs"])
        root.set("xmlns:xsi", self.namespaces["xsi"])

        return root

    def add_header(self, root: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add ReturnHeader element"""
        header = ElementTree.SubElement(root, "ReturnHeader")

        # Add Timestamp
        timestamp = ElementTree.SubElement(header, "Timestamp")
        timestamp.text = datetime.utcnow().isoformat()

        # Add TaxPeriod
        tax_period = ElementTree.SubElement(header, "TaxPeriod")
        tax_period.text = str(data.get("tax_year", datetime.now().year))

        # Add ReturnType
        return_type = ElementTree.SubElement(header, "ReturnType")
        return_type.text = data.get("form_type", "")

    def validate_xml(self, xml_string: str, schema_file: str) -> bool:
        """Validate XML against schema"""
        try:
            schema_doc = etree.parse(f"{self.schema_path}/{schema_file}")
            schema = etree.XMLSchema(schema_doc)

            xml_doc = etree.fromstring(xml_string.encode())
            schema.assertValid(xml_doc)
            return True

        except Exception as e:
            self.logger.error(f"XML validation error: {str(e)}")
            return False

    def prettify_xml(self, elem: ElementTree.Element) -> str:
        """Return a pretty-printed XML string"""
        from xml.dom import minidom

        rough_string = ElementTree.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
