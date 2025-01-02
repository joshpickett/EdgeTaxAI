from typing import Dict, Any, List
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form5329Template(BaseMeFTemplate):
    """Template for Form 5329 (Additional Taxes on Qualified Plans) XML generation"""

    def __init__(self):
        super().__init__()
        self.form_type = "5329"

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 5329 XML"""
        try:
            root = self.create_base_xml()
            self.add_header(root, data)

            # Add Form 5329
            form = ElementTree.SubElement(root, "Form5329")

            # Add taxpayer information
            taxpayer = ElementTree.SubElement(form, "TaxpayerInformation")
            self._add_taxpayer_info(taxpayer, data.get("taxpayer", {}))

            # Add early distribution information
            if data.get("early_distributions"):
                early_dist = ElementTree.SubElement(form, "EarlyDistributions")
                self._add_early_distributions(early_dist, data["early_distributions"])

            # Add excess contribution information
            if data.get("excess_contributions"):
                excess_contrib = ElementTree.SubElement(form, "ExcessContributions")
                self._add_excess_contributions(excess_contrib, data["excess_contributions"])

            xml_string = self.prettify_xml(root)

            # Validate against schema
            if not self.validate_xml(xml_string, "form_5329_2023v1.0.xsd"):
                raise ValueError("Generated Form 5329 XML failed schema validation")

            return xml_string

        except Exception as e:
            self.logger.error(f"Error generating Form 5329: {str(e)}")
            raise

    def _add_taxpayer_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add taxpayer information"""
        name = ElementTree.SubElement(parent, "Name")
        name.text = data.get("name", "")

        ssn = ElementTree.SubElement(parent, "SSN")
        ssn.text = data.get("ssn", "")

        if data.get("spouse"):
            spouse = ElementTree.SubElement(parent, "SpouseInformation")
            spouse_name = ElementTree.SubElement(spouse, "Name")
            spouse_name.text = data["spouse"].get("name", "")
            spouse_ssn = ElementTree.SubElement(spouse, "SSN")
            spouse_ssn.text = data["spouse"].get("ssn", "")

    def _add_early_distributions(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add early distribution information"""
        # Part I - Early Distributions
        distribution_amount = ElementTree.SubElement(parent, "DistributionAmount")
        distribution_amount.text = str(data.get("total_distribution", "0"))

        exceptions = ElementTree.SubElement(parent, "Exceptions")
        exceptions.text = str(data.get("exception_amount", "0"))

        taxable_amount = ElementTree.SubElement(parent, "TaxableAmount")
        taxable_amount.text = str(data.get("taxable_amount", "0"))

        additional_tax = ElementTree.SubElement(parent, "AdditionalTax")
        additional_tax.text = str(data.get("additional_tax", "0"))

        if data.get("exception_codes"):
            exception_codes = ElementTree.SubElement(parent, "ExceptionCodes")
            for code in data["exception_codes"]:
                code_elem = ElementTree.SubElement(exception_codes, "Code")
                code_elem.text = str(code)

    def _add_excess_contributions(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add excess contribution information"""
        # Part III/IV - Excess Contributions
        for account_type, amounts in data.items():
            account = ElementTree.SubElement(parent, f"{account_type}Contributions")
            
            excess_amount = ElementTree.SubElement(account, "ExcessAmount")
            excess_amount.text = str(amounts.get("excess_amount", "0"))

            tax_year = ElementTree.SubElement(account, "TaxYear")
            tax_year.text = str(amounts.get("tax_year", ""))

            if amounts.get("earnings"):
                earnings = ElementTree.SubElement(account, "Earnings")
                earnings.text = str(amounts["earnings"])

            if amounts.get("distribution_date"):
                dist_date = ElementTree.SubElement(account, "DistributionDate")
                dist_date.text = amounts["distribution_date"]

    def calculate_additional_tax(self, distribution_amount: Decimal, exception_amount: Decimal) -> Decimal:
        """Calculate additional tax on early distributions"""
        taxable_amount = distribution_amount - exception_amount
        if taxable_amount <= 0:
            return Decimal("0")
        
        # 10% additional tax rate
        return (taxable_amount * Decimal("0.10")).quantize(Decimal("0.01"))

    def validate_exception_codes(self, codes: List[str]) -> bool:
        """Validate exception codes"""
        valid_codes = {
            "01": "Death",
            "02": "Disability",
            "03": "Medical expenses",
            "04": "Domestic relations order",
            "05": "Series of substantially equal payments",
            "06": "IRA levy",
            "07": "IRA first-time homebuyer",
            "08": "Higher education expenses",
            "09": "Health insurance premiums",
            "10": "Qualified reservist distribution"
        }
        
        return all(code in valid_codes for code in codes)
