from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime


class ScheduleFCalculator:
    """Calculator for Schedule F (Farm Income)"""

    def __init__(self):
        self.expense_categories = {
            "car_truck": "Car and Truck Expenses",
            "chemicals": "Chemicals",
            "conservation": "Conservation Expenses",
            "custom_hire": "Custom Hire",
            "depreciation": "Depreciation",
            "employee_benefit": "Employee Benefits",
            "feed": "Feed",
            "fertilizers": "Fertilizers",
            "freight": "Freight and Trucking",
            "fuel": "Gasoline, Fuel, and Oil",
            "insurance": "Insurance",
            "interest": "Interest",
            "labor": "Labor Hired",
            "pension": "Pension Plans",
            "rent_lease": "Rent or Lease",
            "repairs": "Repairs and Maintenance",
            "seeds": "Seeds and Plants",
            "storage": "Storage and Warehousing",
            "supplies": "Supplies",
            "taxes": "Taxes",
            "utilities": "Utilities",
            "veterinary": "Veterinary, Breeding, and Medicine",
            "other_expenses": "Other Farm Expenses",
        }

    def calculate_totals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Schedule F totals"""
        try:
            # Calculate income totals
            total_income = self._calculate_total_income(data.get("income", {}))

            # Calculate expense totals
            total_expenses = self._calculate_total_expenses(data.get("expenses", {}))

            # Calculate net profit/loss
            net_profit = total_income - total_expenses

            # Calculate self-employment tax
            self_employment_tax = self._calculate_self_employment_tax(net_profit)

            return {
                "gross_income": total_income,
                "total_expenses": total_expenses,
                "net_profit": net_profit,
                "self_employment_tax": self_employment_tax,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as exception:
            raise ValueError(f"Error calculating Schedule F totals: {str(exception)}")

    def _calculate_total_income(self, income_data: Dict[str, Any]) -> Decimal:
        """Calculate total farm income"""
        income_items = [
            "sales_livestock",
            "sales_produce",
            "cooperative_distributions",
            "agricultural_payments",
            "commodity_payments",
            "crop_insurance",
            "custom_hire",
            "other_income",
        ]

        return sum(Decimal(str(income_data.get(item, 0))) for item in income_items)

    def _calculate_total_expenses(self, expense_data: Dict[str, Any]) -> Decimal:
        """Calculate total farm expenses"""
        return sum(
            Decimal(str(expense_data.get(category, 0)))
            for category in self.expense_categories.keys()
        )

    def _calculate_self_employment_tax(self, net_profit: Decimal) -> Decimal:
        """Calculate self-employment tax"""
        if net_profit <= 0:
            return Decimal("0")

        # Calculate self-employment tax (15.3% of 92.35% of net profit)
        taxable_income = net_profit * Decimal("0.9235")
        return taxable_income * Decimal("0.153")

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Schedule F data"""
        errors = []
        warnings = []

        # Validate income data
        if not data.get("income"):
            errors.append("Income data is required")
        else:
            income_data = data["income"]
            for key, value in income_data.items():
                if not isinstance(value, (int, float, Decimal)):
                    errors.append(f"Invalid income value for {key}")
                elif value < 0:
                    warnings.append(f"Negative income value for {key}")

        # Validate expense data
        if not data.get("expenses"):
            errors.append("Expense data is required")
        else:
            expense_data = data["expenses"]
            for key, value in expense_data.items():
                if key not in self.expense_categories:
                    warnings.append(f"Unknown expense category: {key}")
                if not isinstance(value, (int, float, Decimal)):
                    errors.append(f"Invalid expense value for {key}")
                elif value < 0:
                    warnings.append(f"Negative expense value for {key}")

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}
