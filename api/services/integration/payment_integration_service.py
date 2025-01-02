from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.payment.payment_calculator import PaymentCalculator
from api.services.payment.payment_plan_manager import PaymentPlanManager
from api.services.payment.estimated_tax_tracker import EstimatedTaxTracker
from api.services.payment.refund_calculator import RefundCalculator
from api.models.tax_payments import TaxPayments
from api.services.bank_service import BankService  # Assuming BankService is imported


class PaymentIntegrationService:
    """Service for integrating payment-related functionality"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.payment_calculator = PaymentCalculator()
        self.payment_plan_manager = PaymentPlanManager()
        self.estimated_tax_tracker = EstimatedTaxTracker()
        self.refund_calculator = RefundCalculator()
        self.bank_service = BankService()

    async def initialize_payment_options(
        self, user_id: int, form_type: str, tax_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize payment options for form"""
        try:
            # Calculate total tax liability
            tax_calculation = (
                await self.payment_calculator.calculate_total_tax_liability(tax_data)
            )

            # Get payment plan options
            payment_plans = await self.payment_plan_manager.calculate_plan_options(
                tax_calculation["total_tax"]
            )

            # Calculate estimated payments if applicable
            estimated_payments = None
            if tax_data.get("requires_estimated_tax"):
                estimated_payments = (
                    await self.estimated_tax_tracker.calculate_estimated_payment(
                        tax_data
                    )
                )

            # Get bank payment methods
            bank_accounts = await self.bank_service.get_accounts(user_id)
            if bank_accounts:
                payment_methods = self._get_bank_payment_methods(bank_accounts)
            else:
                payment_methods = self._get_available_payment_methods()

            return {
                "tax_calculation": tax_calculation,
                "payment_plans": payment_plans,
                "estimated_payments": estimated_payments,
                "payment_methods": payment_methods,
                "deadlines": self._get_payment_deadlines(tax_data),
            }

        except Exception as e:
            self.logger.error(f"Error initializing payment options: {str(e)}")
            raise

    async def process_payment(
        self, user_id: int, payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process form payment"""
        try:
            payment_type = payment_data.get("payment_type")

            if payment_type == "plan":
                return await self.payment_plan_manager.create_payment_plan(
                    user_id, payment_data
                )
            elif payment_type == "estimated":
                return await self.estimated_tax_tracker.track_payment(
                    user_id, payment_data
                )

            # Calculate payment amount
            payment_calculation = await self.payment_calculator.calculate_payment(
                payment_data
            )

            return {
                "payment_id": payment_calculation["payment_id"],
                "status": "processed",
                "amount": payment_calculation["amount"],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error processing payment: {str(e)}")
            raise

    async def process_bank_payment(
        self, user_id: int, bank_account_id: str, amount: Decimal, payment_type: str
    ) -> Dict[str, Any]:
        """Process payment using bank account"""
        try:
            # Verify bank account
            bank_account = await self.bank_service.verify_account(user_id)
            if not bank_account:
                raise ValueError("Invalid bank account")

            # Process ACH payment
            payment_result = await self.bank_service.initiate_ach_payment(
                user_id, bank_account_id, amount, payment_type
            )

            return payment_result

        except Exception as e:
            self.logger.error(f"Error processing bank payment: {str(e)}")
            raise

    async def calculate_refund(
        self, user_id: int, tax_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate potential refund"""
        try:
            return await self.refund_calculator.calculate_refund(tax_data)
        except Exception as e:
            self.logger.error(f"Error calculating refund: {str(e)}")
            raise

    def _get_available_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods"""
        return [
            {"id": "direct_debit", "name": "Direct Debit", "type": "bank", "fees": 0},
            {
                "id": "credit_card",
                "name": "Credit Card",
                "type": "card",
                "fees": 0.019,  # 1.9% processing fee
            },
            {
                "id": "payment_plan",
                "name": "Payment Plan",
                "type": "installment",
                "fees": 0,
            },
        ]

    def _get_payment_deadlines(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment deadlines"""
        tax_year = tax_data.get("tax_year", datetime.now().year)
        return {
            "filing_deadline": f"{tax_year}-04-15",
            "estimated_deadlines": {
                "q1": f"{tax_year}-04-15",
                "q2": f"{tax_year}-06-15",
                "q3": f"{tax_year}-09-15",
                "q4": f"{tax_year + 1}-01-15",
            },
        }
