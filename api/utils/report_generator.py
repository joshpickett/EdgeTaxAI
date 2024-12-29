import os
import sys
from datetime import datetime
import logging
from api.utils.db_utils import get_db_connection
from api.utils.tax_calculator import TaxCalculator

class ReportGenerator:
    def __init__(self):
        self.db = get_db_connection()
        self.tax_calculator = TaxCalculator()
        
    def generate_quarterly_report(self, user_id: int, quarter: int, year: int) -> Dict[str, Any]:
        """Generate quarterly tax report"""
        try:
            # Get quarterly data
            income = self._get_quarterly_income(user_id, quarter, year)
            expenses = self._get_quarterly_expenses(user_id, quarter, year)
            deductions = self._get_quarterly_deductions(user_id, quarter, year)
            
            # Calculate tax estimates
            tax_estimates = self.tax_calculator.calculate_quarterly_tax(
                income['total'],
                expenses['total']
            )
            
            return {
                'quarter': quarter,
                'year': year,
                'income_summary': income,
                'expense_summary': expenses,
                'deduction_summary': deductions,
                'tax_estimates': tax_estimates,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating quarterly report: {str(e)}")
            raise
            
    def _get_quarterly_income(self, user_id: int, quarter: int, year: int) -> Dict[str, Any]:
        """Get quarterly income data"""
        try:
            cursor = self.db.cursor()
            
            # Get quarter date range
            start_date, end_date = self._get_quarter_dates(quarter, year)
            
            # Query income data
            cursor.execute("""
                SELECT SUM(amount) as total, COUNT(*) as count
                FROM income
                WHERE user_id = ? AND date >= ? AND date <= ?
            """, (user_id, start_date, end_date))
            
            result = cursor.fetchone()
            return {'total': result[0] or 0, 'count': result[1] or 0}
