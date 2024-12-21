from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging
from .db_utils import get_db_connection
import io

class ReportGenerator:
    def __init__(self):
        self.conn = get_db_connection()
        
    def generate_expense_summary(self, user_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate expense summary report"""
        try:
            cursor = self.conn.cursor()
            
            # Get expenses for date range
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE user_id = ? AND date BETWEEN ? AND ?
                GROUP BY category
            """, (user_id, start_date, end_date))
            
            expenses = cursor.fetchall()
            
            # Calculate totals and percentages
            total_expenses = sum(expense['total'] for expense in expenses)
            
            summary = {
                'total_expenses': total_expenses,
                'by_category': {},
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            }
            
            for expense in expenses:
                category = expense['category']
                amount = expense['total']
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                
                summary['by_category'][category] = {
                    'amount': amount,
                    'percentage': round(percentage, 2)
                }
                
            return summary
            
        except Exception as e:
            logging.error(f"Error generating expense summary: {e}")
            raise
            
    def generate_quarterly_report(self, user_id: int, year: int, quarter: int) -> Dict[str, Any]:
        """Generate quarterly tax and expense report"""
        try:
            cursor = self.conn.cursor()
            
            # Calculate quarter date range
            quarter_start = f"{year}-{(quarter-1)*3 + 1:02d}-01"
            quarter_end = f"{year}-{quarter*3:02d}-31"
            
            # Get quarterly expenses
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE user_id = ? AND date BETWEEN ? AND ?
                GROUP BY category
            """, (user_id, quarter_start, quarter_end))
            
            expenses = cursor.fetchall()
            
            # Get quarterly income
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM income
                WHERE user_id = ? AND date BETWEEN ? AND ?
            """, (user_id, quarter_start, quarter_end))
            
            income = cursor.fetchone()['total'] or 0
            
            report = {
                'quarter': quarter,
                'year': year,
                'income': income,
                'expenses': {
                    expense['category']: expense['total']
                    for expense in expenses
                },
                'total_expenses': sum(expense['total'] for expense in expenses),
                'net_income': income - sum(expense['total'] for expense in expenses)
            }
            
            return report
            
        except Exception as e:
            logging.error(f"Error generating quarterly report: {e}")
            raise
            
    def export_to_csv(self, data: Dict[str, Any]) -> str:
        """Export report data to CSV format"""
        try:
            df = pd.DataFrame(data)
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue()
            
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            raise

    def generate_tax_summary(self, user_id: int, year: int) -> Dict[str, Any]:
        """Generate comprehensive tax summary"""
        try:
            cursor = self.conn.cursor()
            
            # Get yearly income
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM income
                WHERE user_id = ? AND strftime('%Y', date) = ?
            """, (user_id, str(year)))
            
            total_income = cursor.fetchone()['total'] or 0
            
            # Get expenses by category
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE user_id = ? AND strftime('%Y', date) = ?
                GROUP BY category
            """, (user_id, str(year)))
            
            expenses = cursor.fetchall()
            
            # Calculate tax deductions
            deductions = sum(expense['total'] for expense in expenses)
            taxable_income = max(0, total_income - deductions)
            
            # Calculate estimated tax (simplified)
            estimated_tax = self._calculate_estimated_tax(taxable_income)
            
            summary = {
                'year': year,
                'total_income': total_income,
                'total_deductions': deductions,
                'taxable_income': taxable_income,
                'estimated_tax': estimated_tax,
                'expenses_by_category': {
                    expense['category']: expense['total']
                    for expense in expenses
                }
            }
            
            return summary
        except Exception as e:
            logging.error(f"Error generating tax summary: {e}")
            raise

    def generate_schedule_c(self, user_id: int, year: int) -> Dict[str, Any]:
        """Generate Internal Revenue Service Schedule C report"""
        try:
            cursor = self.conn.cursor()
            
            # Get business income
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM income
                WHERE user_id = ? AND strftime('%Y', date) = ?
                AND type = 'business'
            """, (user_id, str(year)))
            
            gross_income = cursor.fetchone()['total'] or 0
            
            # Get expenses by Internal Revenue Service category
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE user_id = ? AND strftime('%Y', date) = ?
                AND is_business = 1
                GROUP BY category
            """, (user_id, str(year)))
            
            expenses = cursor.fetchall()
            
            # Format for Schedule C
            schedule_c = {
                'gross_income': gross_income,
                'expenses': {},
                'total_expenses': 0,
                'net_profit': 0
            }
            
            for expense in expenses:
                category = expense['category']
                amount = expense['total']
                schedule_c['expenses'][category] = amount
                schedule_c['total_expenses'] += amount
            
            schedule_c['net_profit'] = gross_income - schedule_c['total_expenses']
            
            return schedule_c
            
        except Exception as e:
            logging.error(f"Error generating Schedule C: {e}")
            raise
            
    def generate_custom_report(
        self, 
        user_id: int, 
        start_date: str, 
        end_date: str,
        categories: List[str],
        report_type: str
    ) -> Dict[str, Any]:
        """Generate custom report based on user specifications"""
        try:
            cursor = self.conn.cursor()
            
            # Base query
            query = """
                SELECT 
                    date,
                    category,
                    description,
                    amount,
                    is_business
                FROM expenses
                WHERE user_id = ? 
                AND date BETWEEN ? AND ?
            """
            
            params = [user_id, start_date, end_date]
            
            # Add category filter if specified
            if categories:
                query += " AND category IN ({})".format(
                    ','.join('?' * len(categories))
                )
                params.extend(categories)
            
            cursor.execute(query, params)
            expenses = cursor.fetchall()
            
            # Format based on report type
            if report_type == 'summary':
                report = {
                    'total_expenses': sum(expense['amount'] for expense in expenses),
                    'by_category': {},
                    'business_expenses': sum(
                        expense['amount'] 
                        for expense in expenses 
                        if expense['is_business']
                    )
                }
                
                for expense in expenses:
                    category = expense['category']
                    if category not in report['by_category']:
                        report['by_category'][category] = 0
                    report['by_category'][category] += expense['amount']
            else:
                report = {
                    'expenses': expenses,
                    'total': sum(expense['amount'] for expense in expenses)
                }
            
            return report
            
        except Exception as e:
            logging.error(f"Error generating custom report: {e}")
            raise

    def generate_analytics(self, user_id: int, year: int) -> Dict[str, Any]:
        """Generate expense pattern analytics"""
        try:
            cursor = self.conn.cursor()
            
            # Get monthly expense patterns
            cursor.execute("""
                SELECT strftime('%m', date) as month,
                       category,
                       SUM(amount) as total
                FROM expenses
                WHERE user_id = ? AND strftime('%Y', date) = ?
                GROUP BY month, category
                ORDER BY month
            """, (user_id, str(year)))
            
            monthly_data = cursor.fetchall()
            
            # Format analytics data
            analytics = {
                'monthly_trends': {},
                'category_trends': {},
                'year_over_year': self._calculate_yoy_comparison(user_id, year)
            }
            
            return analytics
            
        except Exception as e:
            logging.error(f"Error generating analytics: {e}")
            raise
