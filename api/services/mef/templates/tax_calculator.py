from typing import Dict, Any
from decimal import Decimal
from api.config.tax_config import TAX_CONFIG


class TaxCalculationEngine:
    """Enhanced tax calculation engine"""

    def calculate_tax_bracket(
        self, income: Decimal, filing_status: str
    ) -> Dict[str, Any]:
        """Determine tax bracket and calculate tax"""
        brackets = TAX_CONFIG["TAX_BRACKETS"]
        total_tax = Decimal("0")

        for min_income, max_income, rate in brackets:
            if income > min_income:
                taxable_in_bracket = min(income - min_income, max_income - min_income)
                total_tax += taxable_in_bracket * rate

        return {
            "total_tax": total_tax,
            "effective_rate": (total_tax / income).quantize(Decimal(".0001")),
        }

    def determine_standard_deduction(
        self, filing_status: str, age: int, blind: bool
    ) -> Decimal:
        """Calculate standard deduction amount"""
        base_amount = Decimal(str(TAX_CONFIG["STANDARD_DEDUCTION"][filing_status]))

        # Additional amount for age 65+ or blind
        additional = Decimal("0")
        if age >= 65:
            additional += Decimal("1750")  # 2023 additional standard deduction
        if blind:
            additional += Decimal("1750")

        return base_amount + additional

    def calculate_amt(
        self, regular_tax: Decimal, amt_income: Decimal
    ) -> Dict[str, Any]:
        """Calculate Alternative Minimum Tax"""
        amt_exemption = Decimal("75900")  # 2023 AMT exemption
        amt_rate = Decimal("0.26")  # Basic AMT rate

        if amt_income <= amt_exemption:
            return {"amt_liability": Decimal("0")}

        amt_tax = (amt_income - amt_exemption) * amt_rate

        return {
            "amt_liability": max(amt_tax - regular_tax, Decimal("0")),
            "amt_rate": amt_rate,
        }

    def calculate_farm_tax(self, income: Decimal, expenses: Decimal) -> Dict[str, Any]:
        """Calculate tax for farm income"""
        try:
            net_farm_income = income - expenses

            # Calculate self-employment tax for farmers
            self_employment_tax = self._calculate_self_employment_tax(net_farm_income)

            # Calculate regular income tax
            income_tax = self._calculate_income_tax(net_farm_income)

            return {
                "net_farm_income": float(net_farm_income),
                "self_employment_tax": float(self_employment_tax),
                "income_tax": float(income_tax),
                "total_tax": float(self_employment_tax + income_tax),
            }
        except Exception as e:
            self.logger.error(f"Error calculating farm tax: {str(e)}")
            raise
