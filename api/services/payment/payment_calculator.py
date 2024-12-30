from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime
from .estimated_tax_tracker import EstimatedTaxTracker
from .payment_plan_manager import PaymentPlanManager
from api.config.tax_config import TAX_CONFIG

class PaymentCalculator:
    """Calculate tax payments and refunds"""
    
    def __init__(self):
        self.tax_brackets = TAX_CONFIG['TAX_BRACKETS']
        self.self_employment_rate = TAX_CONFIG['SELF_EMPLOYMENT_TAX_RATE']
        self.estimated_tracker = EstimatedTaxTracker(db)
        self.plan_manager = PaymentPlanManager(db)

    async def calculate_total_tax_liability(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total tax liability including all components"""
        try:
            total_income = Decimal(str(income_data.get('total_income', 0)))
            total_deductions = Decimal(str(income_data.get('total_deductions', 0)))
            withholding = Decimal(str(income_data.get('withholding', 0)))
            
            taxable_income = max(total_income - total_deductions, Decimal('0'))
            tax_liability = self._calculate_tax_liability(taxable_income)
            
            # Calculate additional taxes
            self_employment_tax = self._calculate_self_employment_tax(
                income_data.get('self_employment_income', 0)
            ) if income_data.get('is_self_employed') else Decimal('0')
            
            return {
                'income_tax': float(tax_liability),
                'self_employment_tax': float(self_employment_tax),
                'total_tax': float(tax_liability + self_employment_tax)
            }

    def calculate_payment(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required tax payment"""
        total_income = Decimal(str(income_data.get('total_income', 0)))
        total_deductions = Decimal(str(income_data.get('total_deductions', 0)))
        withholding = Decimal(str(income_data.get('withholding', 0)))
        
        taxable_income = max(total_income - total_deductions, Decimal('0'))
        tax_liability = self._calculate_tax_liability(taxable_income)
        
        # Calculate self-employment tax if applicable
        if income_data.get('is_self_employed'):
            self_employment_tax = self._calculate_self_employment_tax(
                income_data.get('self_employment_income', 0)
            )
            tax_liability += self_employment_tax
        
        payment_due = max(tax_liability - withholding, Decimal('0'))
        
        return {
            'tax_liability': float(tax_liability),
            'withholding': float(withholding),
            'payment_due': float(payment_due),
            'calculation_date': datetime.utcnow().isoformat()
        }

    def _calculate_tax_liability(self, taxable_income: Decimal) -> Decimal:
        """Calculate basic tax liability based on brackets"""
        total_tax = Decimal('0')
        
        for min_income, max_income, rate in self.tax_brackets:
            if taxable_income > min_income:
                bracket_income = min(taxable_income - min_income, max_income - min_income)
                total_tax += bracket_income * rate
                
        return total_tax

    def _calculate_self_employment_tax(self, self_employment_income: Decimal) -> Decimal:
        """Calculate self-employment tax"""
        return (Decimal(str(self_employment_income)) * self.self_employment_rate)

    async def calculate_quarterly_estimates(
        self,
        income_data: Dict[str, Any],
        tax_year: int
    ) -> List[Dict[str, Any]]:
        """Calculate quarterly estimated payments"""
        try:
            tax_liability = await self.calculate_total_tax_liability(income_data)
            quarterly_amount = Decimal(str(tax_liability['total_tax'])) / Decimal('4')
            
            return [
                await self.estimated_tracker.calculate_estimated_payment({
                    'projected_income': income_data.get('projected_income'),
                    'previous_payments': income_data.get('previous_payments', 0),
                    'quarter': quarter,
                    'tax_year': tax_year
                }) for quarter in range(1, 5)
            ]
        except Exception as e:
            self.logger.error(f"Error calculating quarterly estimates: {str(e)}")
            raise

    def calculate_estimated_taxes(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate estimated taxes and payment schedule"""
        return self.estimated_tracker.calculate_estimated_payment(
            income_data,
            income_data.get('quarter', 1)
        )

    def get_payment_options(self, amount: Decimal) -> List[Dict[str, Any]]:
        """Get available payment plan options"""
        return self.plan_manager.calculate_plan_options(amount)
