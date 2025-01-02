from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.models.tax_payments import TaxPayments


class PaymentPlanManager:
    """Manage payment plans for tax obligations"""

    def __init__(self, db: Session):
        self.db = db
        self.min_payment = Decimal("25.00")
        self.max_months = 72  # Maximum months allowed for payment plan

    def create_payment_plan(
        self, user_id: int, plan_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new payment plan"""
        total_owed = Decimal(str(plan_data["total_owed"]))
        months = min(int(plan_data.get("months", 12)), self.max_months)

        # Calculate monthly payment
        monthly_payment = max(
            (total_owed / months).quantize(Decimal("0.01")), self.min_payment
        )

        # Generate payment schedule
        schedule = self._generate_schedule(total_owed, monthly_payment, datetime.now())

        # Store payment plan
        plan = {
            "user_id": user_id,
            "total_owed": float(total_owed),
            "monthly_payment": float(monthly_payment),
            "number_of_payments": len(schedule),
            "start_date": datetime.now().isoformat(),
            "schedule": schedule,
        }

        return plan

    def calculate_plan_options(self, total_owed: Decimal) -> List[Dict[str, Any]]:
        """Calculate different payment plan options"""
        options = []

        # Short-term payment plan (6 months or less)
        if total_owed <= Decimal("10000"):
            options.append(self._calculate_short_term_plan(total_owed))

        # Long-term payment plan options
        payment_periods = [12, 24, 36, 48, 60, 72]
        for months in payment_periods:
            if total_owed > self.min_payment * months:
                options.append(self._calculate_long_term_plan(total_owed, months))

        return options

    def track_plan_payment(
        self, user_id: int, payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a payment plan payment"""
        payment = TaxPayments(
            user_id=user_id,
            amount=payment_data["amount"],
            payment_date=datetime.now(),
            tax_year=payment_data["tax_year"],
            payment_type="plan",
            confirmation_number=payment_data.get("confirmation_number"),
        )

        self.db.add(payment)
        self.db.commit()

        return {
            "payment_id": payment.id,
            "status": "recorded",
            "timestamp": payment.payment_date.isoformat(),
        }

    def _calculate_short_term_plan(self, total_owed: Decimal) -> Dict[str, Any]:
        """Calculate short-term payment plan"""
        months = 6
        monthly_payment = (total_owed / months).quantize(Decimal("0.01"))

        return {
            "plan_type": "short-term",
            "months": months,
            "monthly_payment": float(monthly_payment),
            "setup_fee": 0.00,  # No setup fee for short-term plans
            "total_payment": float(total_owed),
        }

    def _calculate_long_term_plan(
        self, total_owed: Decimal, months: int
    ) -> Dict[str, Any]:
        """Calculate long-term payment plan"""
        monthly_payment = (total_owed / months).quantize(Decimal("0.01"))
        setup_fee = Decimal("31.00")  # Standard setup fee for direct debit

        return {
            "plan_type": "long-term",
            "months": months,
            "monthly_payment": float(monthly_payment),
            "setup_fee": float(setup_fee),
            "total_payment": float(total_owed + setup_fee),
        }

    def _generate_schedule(
        self, total_amount: Decimal, monthly_payment: Decimal, start_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate payment schedule"""
        schedule = []
        remaining = total_amount
        payment_date = start_date

        while remaining > 0:
            payment = min(monthly_payment, remaining)
            schedule.append(
                {
                    "payment_number": len(schedule) + 1,
                    "date": payment_date.isoformat(),
                    "amount": float(payment),
                    "remaining_balance": float(remaining - payment),
                }
            )

            remaining -= payment
            payment_date += timedelta(days=30)

        return schedule
