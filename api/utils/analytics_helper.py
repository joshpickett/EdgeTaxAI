from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .db_utils import Database
from .tax_calculator import TaxCalculator
from .trip_analyzer import TripAnalyzer

class AnalyticsHelper:
    def __init__(self, db: Database):
        self.db = db
        self.tax_calculator = TaxCalculator()
        self.trip_analyzer = TripAnalyzer(db)
        self.logger = logging.getLogger(__name__)

    def get_earnings_summary(self, user_id: int, 
                           period: Optional[tuple] = None) -> Dict[str, any]:
        """Generate earnings summary for a user."""
        try:
            query = """
                SELECT platform, SUM(amount) as total_amount, COUNT(*) as transaction_count
                FROM earnings
                WHERE user_id = ?
            """
            params = [user_id]

            if period:
                query += " AND date BETWEEN ? AND ?"
                params.extend(period)

            query += " GROUP BY platform"

            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                platform_earnings = cursor.fetchall()

            total_earnings = sum(p['total_amount'] for p in platform_earnings)
            
            return {
                'total_earnings': round(total_earnings, 2),
                'platform_breakdown': [
                    {
                        'platform': p['platform'],
                        'amount': round(p['total_amount'], 2),
                        'percentage': round(p['total_amount'] / total_earnings * 100, 2),
                        'transaction_count': p['transaction_count']
                    }
                    for p in platform_earnings
                ],
                'average_per_transaction': round(
                    total_earnings / sum(p['transaction_count'] for p in platform_earnings)
                    if platform_earnings else 0, 2
                )
            }

        except Exception as e:
            self.logger.error(f"Error generating earnings summary: {str(e)}")
            raise

    def get_expense_analysis(self, user_id: int, 
                           period: Optional[tuple] = None) -> Dict[str, any]:
        """Analyze expenses by category."""
        try:
            query = """
                SELECT category, SUM(amount) as total_amount, COUNT(*) as count
                FROM expenses
                WHERE user_id = ?
            """
            params = [user_id]

            if period:
                query += " AND date BETWEEN ? AND ?"
                params.extend(period)

            query += " GROUP BY category"

            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                expenses = cursor.fetchall()

            total_expenses = sum(e['total_amount'] for e in expenses)
            
            return {
                'total_expenses': round(total_expenses, 2),
                'category_breakdown': [
                    {
                        'category': e['category'],
                        'amount': round(e['total_amount'], 2),
                        'percentage': round(e['total_amount'] / total_expenses * 100, 2),
                        'transaction_count': e['count']
                    }
                    for e in expenses
                ],
                'average_per_category': round(
                    total_expenses / len(expenses) if expenses else 0, 2
                )
            }

        except Exception as e:
            self.logger.error(f"Error analyzing expenses: {str(e)}")
            raise

    def get_comprehensive_report(self, user_id: int, 
                               period: Optional[tuple] = None) -> Dict[str, any]:
        """Generate comprehensive financial report."""
        try:
            earnings = self.get_earnings_summary(user_id, period)
            expenses = self.get_expense_analysis(user_id, period)
            trips = self.trip_analyzer.analyze_trip_patterns(user_id, period)
            
            net_income = earnings['total_earnings'] - expenses['total_expenses']
            tax_summary = self.tax_calculator.get_tax_summary(
                earnings['total_earnings'],
                expenses['category_breakdown'],
                trips['total_miles']
            )

            return {
                'earnings_summary': earnings,
                'expense_analysis': expenses,
                'trip_analysis': trips,
                'tax_summary': tax_summary,
                'net_income': round(net_income, 2),
                'profit_margin': round(
                    net_income / earnings['total_earnings'] * 100 
                    if earnings['total_earnings'] > 0 else 0, 2
                )
            }

        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {str(e)}")
            raise
