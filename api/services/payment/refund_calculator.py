from decimal import Decimal
from typing import Dict, Any
from datetime import datetime
from api.models.tax_payments import TaxPayments
from sqlalchemy.orm import Session

class RefundCalculator:
    """Calculate tax refunds"""
    
    def calculate_refund(self, 
                        tax_data: Dict[str, Any],
                        db: Session) -> Dict[str, Any]:
        """Calculate potential refund amount"""
        total_tax = Decimal(str(tax_data.get('total_tax', 0)))
        total_payments = self._get_total_payments(tax_data['user_id'], 
                                                tax_data['tax_year'],
                                                db)
        
        difference = total_payments - total_tax
        
        return {
            'refund_amount': float(max(difference, Decimal('0'))),
            'owed_amount': float(max(-difference, Decimal('0'))),
            'total_payments': float(total_payments),
            'total_tax': float(total_tax),
            'calculation_date': datetime.utcnow().isoformat()
        }

    def _get_total_payments(self, 
                           user_id: int, 
                           tax_year: int,
                           db: Session) -> Decimal:
        """Get total payments made for tax year"""
        payments = db.query(TaxPayments).filter(
            TaxPayments.user_id == user_id,
            TaxPayments.tax_year == tax_year
        ).all()
        
        return sum(Decimal(str(payment.amount)) for payment in payments)

    def validate_direct_deposit(self, bank_info: Dict[str, Any]) -> Dict[str, bool]:
        """Validate direct deposit information"""
        routing_number = bank_info.get('routing_number', '')
        account_number = bank_info.get('account_number', '')
        
        return {
            'is_valid': self._validate_routing_number(routing_number) and \
                       self._validate_account_number(account_number),
            'routing_valid': self._validate_routing_number(routing_number),
            'account_valid': self._validate_account_number(account_number)
        }

    def _validate_routing_number(self, routing_number: str) -> bool:
        """Validate routing number using American Bankers Association checksum"""
        if not routing_number.isdigit() or len(routing_number) != 9:
            return False
            
        digits = [int(d) for d in routing_number]
        checksum = (
            3 * (digits[0] + digits[3] + digits[6]) +
            7 * (digits[1] + digits[4] + digits[7]) +
            (digits[2] + digits[5] + digits[8])
        ) % 10
        
        return checksum == 0

    def _validate_account_number(self, account_number: str) -> bool:
        """Validate account number format"""
        return account_number.isdigit() and 4 <= len(account_number) <= 17
