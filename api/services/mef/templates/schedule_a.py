from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_schedule_template import BaseScheduleTemplate


class ScheduleATemplate(BaseScheduleTemplate):
    """Template for Schedule A (Itemized Deductions) XML generation"""

    def __init__(self):
        super().__init__()
        self.schedule_type = "A"

    def _add_schedule_content(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add Schedule A specific content"""
        deductions = data.get("deductions", {})

        # Medical and Dental Expenses
        medical = ElementTree.SubElement(parent, "MedicalAndDental")
        self._add_medical_expenses(medical, deductions.get("medical", {}))

        # Taxes Paid
        taxes = ElementTree.SubElement(parent, "TaxesPaid")
        self._add_taxes_paid(taxes, deductions.get("taxes", {}))

        # Interest Paid
        interest = ElementTree.SubElement(parent, "InterestPaid")
        self._add_interest_paid(interest, deductions.get("interest", {}))

        # Gifts to Charity
        charity = ElementTree.SubElement(parent, "Charity")
        self._add_charitable_contributions(charity, deductions.get("charity", {}))

        # Casualty and Theft Losses
        casualty = ElementTree.SubElement(parent, "CasualtyAndTheft")
        self._add_casualty_losses(casualty, deductions.get("casualty", {}))

        # Job Expenses and Miscellaneous
        misc = ElementTree.SubElement(parent, "Miscellaneous")
        self._add_miscellaneous_deductions(misc, deductions.get("miscellaneous", {}))

    def _add_medical_expenses(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add medical and dental expenses"""
        total = ElementTree.SubElement(parent, "TotalExpenses")
        total.text = str(data.get("total", "0.00"))

        insurance = ElementTree.SubElement(parent, "Insurance")
        insurance.text = str(data.get("insurance", "0.00"))

        providers = ElementTree.SubElement(parent, "Providers")
        providers.text = str(data.get("providers", "0.00"))

    def _add_taxes_paid(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add taxes paid"""
        state_local = ElementTree.SubElement(parent, "StateLocalTaxes")
        state_local.text = str(data.get("state_local", "0.00"))

        real_estate = ElementTree.SubElement(parent, "RealEstateTaxes")
        real_estate.text = str(data.get("real_estate", "0.00"))

        personal_property = ElementTree.SubElement(parent, "PersonalPropertyTaxes")
        personal_property.text = str(data.get("personal_property", "0.00"))

    def _add_interest_paid(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add interest paid"""
        mortgage = ElementTree.SubElement(parent, "HomeMortgage")
        mortgage.text = str(data.get("mortgage", "0.00"))

        points = ElementTree.SubElement(parent, "Points")
        points.text = str(data.get("points", "0.00"))

        investment = ElementTree.SubElement(parent, "InvestmentInterest")
        investment.text = str(data.get("investment", "0.00"))

    def _add_charitable_contributions(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add charitable contributions"""
        cash = ElementTree.SubElement(parent, "CashContributions")
        cash.text = str(data.get("cash", "0.00"))

        noncash = ElementTree.SubElement(parent, "NonCashContributions")
        noncash.text = str(data.get("noncash", "0.00"))

        carryover = ElementTree.SubElement(parent, "Carryover")
        carryover.text = str(data.get("carryover", "0.00"))

    def _add_casualty_losses(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add casualty and theft losses"""
        total = ElementTree.SubElement(parent, "TotalLoss")
        total.text = str(data.get("total", "0.00"))

        insurance_reimbursement = ElementTree.SubElement(
            parent, "InsuranceReimbursement"
        )
        insurance_reimbursement.text = str(data.get("insurance_reimbursement", "0.00"))

    def _add_miscellaneous_deductions(
        self, parent: ElementTree.Element, data: Dict[str, Any]
    ) -> None:
        """Add miscellaneous deductions"""
        job_expenses = ElementTree.SubElement(parent, "JobExpenses")
        job_expenses.text = str(data.get("job_expenses", "0.00"))

        tax_prep = ElementTree.SubElement(parent, "TaxPrepFees")
        tax_prep.text = str(data.get("tax_prep", "0.00"))

        other = ElementTree.SubElement(parent, "OtherExpenses")
        other.text = str(data.get("other", "0.00"))
