from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_schedule_template import BaseScheduleTemplate


class ScheduleBTemplate(BaseScheduleTemplate):
    """Template for Schedule B (Interest and Dividends) XML generation"""

    def __init__(self):
        super().__init__()
        self.schedule_type = "B"

    def _add_schedule_content(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add Schedule B specific content"""
        # Part I - Interest
        interest = ElementTree.SubElement(parent, "InterestIncome")
        self._add_interest_income(interest, data.get("interest", {}))

        # Part II - Ordinary Dividends
        dividends = ElementTree.SubElement(parent, "OrdinaryDividends")
        self._add_dividend_income(dividends, data.get("dividends", {}))

        # Part III - Foreign Accounts and Trusts
        foreign = ElementTree.SubElement(parent, "ForeignAccounts")
        self._add_foreign_accounts(foreign, data.get("foreign_accounts", {}))

    def _add_interest_income(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add interest income section"""
        # List of interest payers
        payers = ElementTree.SubElement(parent, "Payers")
        for payer_data in data.get("payers", []):
            payer = ElementTree.SubElement(payers, "Payer")

            name = ElementTree.SubElement(payer, "Name")
            name.text = payer_data.get("name", "")

            amount = ElementTree.SubElement(payer, "Amount")
            amount.text = str(payer_data.get("amount", "0.00"))

        # Total interest
        total = ElementTree.SubElement(parent, "TotalInterest")
        total.text = str(data.get("total_interest", "0.00"))

    def _add_dividend_income(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add dividend income section"""
        # List of dividend payers
        payers = ElementTree.SubElement(parent, "Payers")
        for payer_data in data.get("payers", []):
            payer = ElementTree.SubElement(payers, "Payer")

            name = ElementTree.SubElement(payer, "Name")
            name.text = payer_data.get("name", "")

            amount = ElementTree.SubElement(payer, "Amount")
            amount.text = str(payer_data.get("amount", "0.00"))

        # Total dividends
        total = ElementTree.SubElement(parent, "TotalDividends")
        total.text = str(data.get("total_dividends", "0.00"))

    def _add_foreign_accounts(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add foreign accounts and trusts section"""
        has_foreign = ElementTree.SubElement(parent, "HasForeignAccounts")
        has_foreign.text = str(data.get("has_foreign_accounts", False)).lower()

        if data.get("has_foreign_accounts"):
            countries = ElementTree.SubElement(parent, "Countries")
            for country in data.get("countries", []):
                country_elem = ElementTree.SubElement(countries, "Country")
                country_elem.text = country

            max_value = ElementTree.SubElement(parent, "MaximumValue")
            max_value.text = str(data.get("maximum_value", "0.00"))
