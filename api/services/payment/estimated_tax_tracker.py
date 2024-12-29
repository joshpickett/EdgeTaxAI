from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.tax_payments import TaxPayments
from api.config.tax_config import TAX_CONFIG

class EstimatedTaxTracker:
    """Track and manage estimated tax payments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.quarterly_deadlines = TAX_CONFIG['QUARTERLY_DEADLINES']
        self.quarterly_periods = TAX_CONFIG['QUARTERLY_PERIODS']

    def calculate_estimated_payment(self, income_data: Dict[str, Any], quarter: int) -> Dict[str, Any]:
        """Calculate estimated quarterly payment"""
        total_income = Decimal(str(income_data.get('projected_income', 0)))
        total_deductions = Decimal(str(income_data.get('projected_deductions', 0)))
        previous_payments = Decimal(str(income_data.get('previous_payments', 0)))
        
        # Calculate estimated tax
        taxable_income = max(total_income - total_deductions, Decimal('0'))
        estimated_tax = self._calculate_estimated_tax(taxable_income)
        
        # Calculate quarterly amount
        quarterly_amount = (estimated_tax - previous_payments) / (5 - quarter)
        
        return {
            'quarter': quarter,
            'payment_amount': float(max(quarterly_amount, Decimal('0'))),
            'due_date': self._get_due_date(quarter),
            'period': self.quarterly_periods[quarter],
            'estimated_annual_tax': float(estimated_tax)
        }

    def track_payment(self, 
                     user_id: int, 
                     payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record an estimated tax payment"""
        payment = TaxPayments(
            user_id=user_id,
            amount=payment_data['amount'],
            payment_date=datetime.now(),
            tax_year=payment_data['tax_year'],
            quarter=payment_data['quarter'],
            payment_type='estimated',
            confirmation_number=payment_data.get('confirmation_number')
        )
        
        self.db.add(payment)
        self.db.commit()
        
        return {
            'payment_id': payment.id,
            'status': 'recorded',
            'timestamp': payment.payment_date.isoformat()
        }

    def get_payment_history(self, 
                          user_id: int, 
                          tax_year: int) -> List[Dict[str, Any]]:
        """Get estimated tax payment history"""
        payments = self.db.query(TaxPayments).filter(
            TaxPayments.user_id == user_id,
            TaxPayments.tax_year == tax_year,
            TaxPayments.payment_type == 'estimated'
        ).all()
        
        return [{
            'payment_id': payment.id,
            'amount': float(payment.amount),
            'date': payment.payment_date.isoformat(),
            'quarter': payment.quarter,
            'confirmation_number': payment.confirmation_number
        } for payment in payments]

    def get_payment_schedule(self, 
                           user_id: int, 
                           tax_year: int) -> List[Dict[str, Any]]:
        """Get payment schedule with deadlines"""
        payments = self.get_payment_history(user_id, tax_year)
        schedule = []
        
        for quarter, deadline in self.quarterly_deadlines.items():
            quarter_payments = [p for p in payments if p['quarter'] == quarter]
            total_paid = sum(p['amount'] for p in quarter_payments)
            
            schedule.append({
                'quarter': quarter,
                'deadline': f"{tax_year}-{deadline}",
                'paid_amount': float(total_paid),
                'payments': quarter_payments,
                'status': 'paid' if quarter_payments else 'pending'
            })
        
        return schedule

    def _calculate_estimated_tax(self, taxable_income: Decimal) -> Decimal:
        """Calculate estimated annual tax"""
        total_tax = Decimal('0')
        
        for min_income, max_income, rate in TAX_CONFIG['TAX_BRACKETS']:
            if taxable_income > min_income:
                bracket_income = min(taxable_income - min_income, max_income - min_income)
                total_tax += bracket_income * rate
        
        return total_tax

    def _get_due_date(self, quarter: int) -> str:
        """Get due date for quarter"""
        current_year = datetime.now().year
        month_day = self.quarterly_deadlines[quarter]
        
        # Handle Q4 payment due in next year
        if quarter == 4:
            return f"{current_year + 1}-{month_day}"
        return f"{current_year}-{month_day}"
