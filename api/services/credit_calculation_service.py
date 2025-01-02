from typing import Dict, Any, List
import logging
from decimal import Decimal
from datetime import datetime
from api.models.credits import Credits
from api.utils.tax_calculator import TaxCalculator


class CreditCalculationService:
    """Service for calculating and validating tax credits"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.calculator = TaxCalculator()
        self.credit_limits = {
            # Add farm-specific credit limits
            "farm_credits": {
                "max_credit": Decimal("5000"),
                "income_limit": Decimal("400000")
            },
            "child_tax_credit": {
                "amount_per_child": Decimal("2000"),
                "income_limit_single": Decimal("200000"),
                "income_limit_joint": Decimal("400000"),
                "refundable_portion": Decimal("1400"),
            },
            "earned_income_credit": {
                "max_amount_0": Decimal("560"),
                "max_amount_1": Decimal("3584"),
                "max_amount_2": Decimal("5920"),
                "max_amount_3": Decimal("6728"),
                "income_limit_0": Decimal("16480"),
                "income_limit_1": Decimal("43492"),
                "income_limit_2": Decimal("49399"),
                "income_limit_3": Decimal("53057"),
            },
        }

    async def calculate_available_credits(
        self, user_id: int, tax_year: int
    ) -> Dict[str, Any]:
        """Calculate all available tax credits"""
        try:
            tax_data = await self._get_tax_data(user_id, tax_year)

            credits = {
                "child_tax_credit": self._calculate_child_tax_credit(tax_data),
                "earned_income_credit": self._calculate_earned_income_credit(tax_data),
                "farm_credits": self._calculate_farm_credits(tax_data),
                "education_credits": self._calculate_education_credits(tax_data),
            }

            return {
                "available_credits": credits,
                "total_credits": sum(c["amount"] for c in credits.values()),
                "qualifications": self._generate_qualification_summary(credits),
            }

        except Exception as e:
            self.logger.error(f"Error calculating credits: {str(e)}")
            raise

    def _calculate_child_tax_credit(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Child Tax Credit"""
        try:
            qualifying_children = tax_data.get("dependents", {}).get(
                "qualifying_children", 0
            )
            income = Decimal(str(tax_data.get("adjusted_gross_income", 0)))
            filing_status = tax_data.get("filing_status")

            # Determine income limit based on filing status
            income_limit = (
                self.credit_limits["child_tax_credit"]["income_limit_joint"]
                if filing_status == "married_filing_jointly"
                else self.credit_limits["child_tax_credit"]["income_limit_single"]
            )

            # Calculate base credit
            base_credit = (
                qualifying_children
                * self.credit_limits["child_tax_credit"]["amount_per_child"]
            )

            # Apply income phase-out
            if income > income_limit:
                reduction = ((income - income_limit) / Decimal("1000")).quantize(
                    Decimal("1.")
                ) * Decimal("50")
                base_credit = max(Decimal("0"), base_credit - reduction)

            return {
                "amount": base_credit,
                "refundable_amount": min(
                    base_credit,
                    self.credit_limits["child_tax_credit"]["refundable_portion"],
                ),
                "qualifying_children": qualifying_children,
            }

        except Exception as e:
            self.logger.error(f"Error calculating child tax credit: {str(e)}")
            raise

    def _calculate_earned_income_credit(
        self, tax_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate Earned Income Credit"""
        try:
            earned_income = Decimal(str(tax_data.get("earned_income", 0)))
            qualifying_children = tax_data.get("dependents", {}).get(
                "qualifying_children", 0
            )

            # Get appropriate income limit and maximum credit
            max_amount_key = f"max_amount_{min(qualifying_children, 3)}"
            income_limit_key = f"income_limit_{min(qualifying_children, 3)}"

            max_credit = self.credit_limits["earned_income_credit"][max_amount_key]
            income_limit = self.credit_limits["earned_income_credit"][income_limit_key]

            # Calculate credit
            if earned_income > income_limit:
                return {
                    "amount": Decimal("0"),
                    "qualifying_children": qualifying_children,
                }

            credit_percentage = self._get_eic_percentage(qualifying_children)
            calculated_credit = (earned_income * credit_percentage).quantize(
                Decimal("0.01")
            )

            return {
                "amount": min(calculated_credit, max_credit),
                "qualifying_children": qualifying_children,
                "earned_income": earned_income,
            }

        except Exception as e:
            self.logger.error(f"Error calculating earned income credit: {str(e)}")
            raise

    def _calculate_farm_credits(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate farm-related credits"""
        try:
            farm_income = Decimal(str(tax_data.get("farm_income", {}).get("total_income", 0)))
            agricultural_payments = Decimal(str(tax_data.get("agricultural_payments", 0)))
            farm_expenses = Decimal(str(tax_data.get("farm_expenses", 0)))

            # Calculate base credit
            base_credit = min(
                self.credit_limits["farm_credits"]["max_credit"],
                (farm_income + agricultural_payments) * Decimal("0.10")
            )

            # Apply income phase-out
            income = Decimal(str(tax_data.get("adjusted_gross_income", 0)))
            income_limit = self.credit_limits["farm_credits"]["income_limit"]

            if income > income_limit:
                reduction = ((income - income_limit) / Decimal("1000")).quantize(
                    Decimal("1.")
                ) * Decimal("50")
                base_credit = max(Decimal("0"), base_credit - reduction)

            return {
                "amount": base_credit,
                "farm_income": farm_income,
                "agricultural_payments": agricultural_payments
            }

        except Exception as e:
            self.logger.error(f"Error calculating farm credits: {str(e)}")
            raise

    def _calculate_education_credits(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Education Credits"""
        try:
            education_expenses = Decimal(
                str(tax_data.get("education", {}).get("qualified_expenses", 0))
            )

            if education_expenses == 0:
                return {"amount": Decimal("0")}

            # Calculate American Opportunity Credit
            american_opportunity_credit_amount = min(
                education_expenses, Decimal("4000")
            ) * Decimal("0.25")

            # Calculate Lifetime Learning Credit
            lifetime_learning_credit_amount = min(
                education_expenses, Decimal("10000")
            ) * Decimal("0.2")

            # Return the more beneficial credit
            if american_opportunity_credit_amount > lifetime_learning_credit_amount:
                return {
                    "amount": american_opportunity_credit_amount,
                    "type": "american_opportunity",
                    "qualified_expenses": education_expenses,
                }
            else:
                return {
                    "amount": lifetime_learning_credit_amount,
                    "type": "lifetime_learning",
                    "qualified_expenses": education_expenses,
                }

        except Exception as e:
            self.logger.error(f"Error calculating education credits: {str(e)}")
            raise

    def _get_eic_percentage(self, qualifying_children: int) -> Decimal:
        """Get Earned Income Credit percentage based on number of qualifying children"""
        percentages = {
            0: Decimal("0.0765"),
            1: Decimal("0.3400"),
            2: Decimal("0.4000"),
            3: Decimal("0.4500"),
        }
        return percentages.get(min(qualifying_children, 3), Decimal("0.4500"))

    def _generate_qualification_summary(
        self, credits: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate qualification summary for all credits"""
        return {
            "qualified_credits": [
                name for name, data in credits.items() if data.get("amount", 0) > 0
            ],
            "total_qualified": sum(
                1 for data in credits.values() if data.get("amount", 0) > 0
            ),
            "requirements_met": {
                name: self._check_requirements(name, data)
                for name, data in credits.items()
            },
        }

    def _check_requirements(
        self, credit_type: str, credit_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check if all requirements are met for a specific credit"""
        requirements = {
            "child_tax_credit": {
                "has_qualifying_children": credit_data.get("qualifying_children", 0)
                > 0,
                "meets_income_requirements": credit_data.get("amount", 0) > 0,
            },
            "earned_income_credit": {
                "has_earned_income": credit_data.get("earned_income", 0) > 0,
                "meets_income_limits": credit_data.get("amount", 0) > 0,
            },
            "farm_credits": {
                "has_farm_income": credit_data.get("farm_income", 0) > 0,
                "meets_income_limits": credit_data.get("amount", 0) > 0,
            },
            "education_credits": {
                "has_qualified_expenses": credit_data.get("qualified_expenses", 0) > 0
            },
        }
        return requirements.get(credit_type, {})

    async def _get_tax_data(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Get tax data for credit calculations"""
        # Implementation would fetch actual tax data
        # This is a placeholder
        return {
            "adjusted_gross_income": 50000,
            "earned_income": 45000,
            "filing_status": "single",
            "dependents": {"qualifying_children": 2},
            "education": {"qualified_expenses": 4000},
            "farm_income": {"total_income": 30000},
            "agricultural_payments": 2000,
            "farm_expenses": 1000,
        }
