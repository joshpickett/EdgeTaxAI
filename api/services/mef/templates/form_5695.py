from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form5695Template(BaseMeFTemplate):
    """Template for Form 5695 (Residential Energy Credits)"""

    def __init__(self):
        super().__init__()
        self.form_type = "Form5695"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 5695 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)

        # Add Form 5695
        form = ElementTree.SubElement(root, "Form5695")

        # Add residential energy efficient property credit
        energy_property = ElementTree.SubElement(form, "EnergyEfficientProperty")
        self._add_energy_property_credit(energy_property, data.get("energy_property", {}))

        # Add nonbusiness energy property credit
        nonbusiness_property = ElementTree.SubElement(form, "NonbusinessEnergy")
        self._add_nonbusiness_credit(nonbusiness_property, data.get("nonbusiness_property", {}))

        xml_string = self.prettify_xml(root)

        # Validate against schema
        if not self.validate_xml(xml_string, "5695_2023v1.0.xsd"):
            raise ValueError("Generated XML failed schema validation")

        return xml_string

    def _add_energy_property_credit(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add energy efficient property credit information"""
        solar_electric = ElementTree.SubElement(parent, "SolarElectric")
        solar_electric.text = str(data.get("solar_electric", "0.00"))

        solar_water = ElementTree.SubElement(parent, "SolarWater")
        solar_water.text = str(data.get("solar_water", "0.00"))

        fuel_cell = ElementTree.SubElement(parent, "FuelCell")
        fuel_cell.text = str(data.get("fuel_cell", "0.00"))

        small_wind = ElementTree.SubElement(parent, "SmallWind")
        small_wind.text = str(data.get("small_wind", "0.00"))

        geothermal = ElementTree.SubElement(parent, "Geothermal")
        geothermal.text = str(data.get("geothermal", "0.00"))

        total_cost = ElementTree.SubElement(parent, "TotalCost")
        total_cost.text = str(data.get("total_cost", "0.00"))

        credit_amount = ElementTree.SubElement(parent, "CreditAmount")
        credit_amount.text = str(data.get("credit_amount", "0.00"))

    def _add_nonbusiness_credit(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add nonbusiness energy property credit information"""
        insulation = ElementTree.SubElement(parent, "Insulation")
        self._add_improvement_details(insulation, data.get("insulation", {}))

        windows = ElementTree.SubElement(parent, "Windows")
        self._add_improvement_details(windows, data.get("windows", {}))

        heating_ventilation_air_conditioning = ElementTree.SubElement(parent, "HeatingVentilationAirConditioning")
        self._add_improvement_details(heating_ventilation_air_conditioning, data.get("hvac", {}))

        total_cost = ElementTree.SubElement(parent, "TotalCost")
        total_cost.text = str(data.get("total_cost", "0.00"))

        credit_amount = ElementTree.SubElement(parent, "CreditAmount")
        credit_amount.text = str(data.get("credit_amount", "0.00"))

    def _add_improvement_details(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add improvement details"""
        cost = ElementTree.SubElement(parent, "Cost")
        cost.text = str(data.get("cost", "0.00"))

        installation = ElementTree.SubElement(parent, "Installation")
        installation.text = str(data.get("installation", "0.00"))

        manufacturer = ElementTree.SubElement(parent, "Manufacturer")
        manufacturer.text = data.get("manufacturer", "")

        energy_certification = ElementTree.SubElement(parent, "EnergyCertification")
        energy_certification.text = str(data.get("energy_certification", False)).lower()
