from typing import Dict, Any, List
import logging
from decimal import Decimal
from api.models.tax_forms import TaxForms
from api.services.mef.cross_schedule_calculator import CrossScheduleCalculator


class ScheduleSummaryService:
    """Service for generating comprehensive schedule summaries"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.calculator = CrossScheduleCalculator()

    async def generate_summary(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Generate comprehensive schedule summary"""
        try:
            schedules = await self._get_user_schedules(user_id, tax_year)

            # Calculate totals across schedules
            totals = await self.calculator.calculate_totals(schedules)

            # Validate consistency between schedules
            validation = await self.calculator.validate_consistency(schedules)

            return {
                "schedules": self._summarize_schedules(schedules),
                "totals": totals,
                "validation": validation,
                "recommendations": self._generate_recommendations(schedules, totals),
            }

        except Exception as e:
            self.logger.error(f"Error generating schedule summary: {str(e)}")
            raise

    def _summarize_schedules(self, schedules: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for each schedule"""
        summaries = {}

        for schedule_type, data in schedules.items():
            if schedule_type == "SCHEDULE_C":
                summaries[schedule_type] = self._summarize_schedule_c(data)
            elif schedule_type == "SCHEDULE_E":
                summaries[schedule_type] = self._summarize_schedule_e(data)
            # Add more schedule types as needed

        return summaries

    def _summarize_schedule_c(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schedule C summary"""
        income = Decimal(str(data.get("income", {}).get("gross_receipts", 0)))
        expenses = sum(
            Decimal(str(amount)) for amount in data.get("expenses", {}).values()
        )

        return {
            "gross_income": income,
            "total_expenses": expenses,
            "net_profit": income - expenses,
            "expense_categories": self._summarize_expense_categories(
                data.get("expenses", {})
            ),
        }

    def _summarize_schedule_e(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schedule E summary"""
        properties = data.get("properties", [])
        total_income = Decimal("0")
        total_expenses = Decimal("0")

        for prop in properties:
            total_income += sum(
                Decimal(str(amount)) for amount in prop.get("income", {}).values()
            )
            total_expenses += sum(
                Decimal(str(amount)) for amount in prop.get("expenses", {}).values()
            )

        return {
            "total_properties": len(properties),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": total_income - total_expenses,
            "property_summaries": [self._summarize_property(p) for p in properties],
        }

    def _summarize_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for individual property"""
        income = sum(
            Decimal(str(amount)) for amount in property_data.get("income", {}).values()
        )
        expenses = sum(
            Decimal(str(amount))
            for amount in property_data.get("expenses", {}).values()
        )

        return {
            "address": property_data.get("address", {}),
            "income": income,
            "expenses": expenses,
            "net_income": income - expenses,
        }

    def _summarize_expense_categories(self, expenses: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize expenses by category"""
        categories = {
            "advertising": Decimal("0"),
            "vehicle": Decimal("0"),
            "insurance": Decimal("0"),
            "utilities": Decimal("0"),
            "other": Decimal("0"),
        }

        for category, amount in expenses.items():
            if category in categories:
                categories[category] += Decimal(str(amount))
            else:
                categories["other"] += Decimal(str(amount))

        return categories

    def _generate_recommendations(
        self, schedules: Dict[str, Any], totals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on schedule analysis"""
        recommendations = []

        # Check expense ratios
        if totals.get("total_expenses", 0) > 0:
            expense_ratio = (
                totals["total_expenses"] / totals["total_income"]
                if totals.get("total_income", 0) > 0
                else 0
            )

            if expense_ratio > Decimal("0.7"):
                recommendations.append(
                    {
                        "type": "expense_ratio",
                        "message": "High expense ratio detected. Review expenses for accuracy.",
                        "priority": "high",
                    }
                )

        # Add more recommendation logic as needed

        return recommendations

    async def _get_user_schedules(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Get user's tax schedules"""
        # Implementation would fetch actual schedules
        # This is a placeholder
        return {}
