from typing import Dict, Any, List
from datetime import datetime
import logging
from api.utils.tax_calculator import TaxCalculator
from api.utils.db_utils import get_db_connection
from api.utils.cache_utils import CacheManager, cache_response
from api.utils.error_handler import ReportGenerationError

cache_manager = CacheManager()
tax_calculator = TaxCalculator()

class ReportService:
    def __init__(self):
        self.db = get_db_connection()
        self.cache = CacheManager()

    @cache_response(timeout=3600)
    def generate_tax_summary(self, user_id: int, year: int) -> Dict[str, Any]:
        """Generate tax summary report"""
        try:
            cached_data = self.cache.get_report_cache(user_id, 'tax_summary', {'year': year})
            if cached_data:
                return cached_data

            cursor = self.db.cursor()
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses 
                WHERE user_id = ? AND strftime('%Y', date) = ?
                GROUP BY category
            """, (user_id, str(year)))
            
            expenses = cursor.fetchall()
            report_data = {
                'summary': expenses,
                'year': year,
                'generated_at': datetime.now().isoformat()
            }
            self.cache.set_report_cache(user_id, 'tax_summary', {'year': year}, report_data)
            return report_data
        except Exception as e:
            raise ReportGenerationError("Failed to generate tax summary", 
                                        "tax_summary", {"error": str(e)})

    @cache_response(timeout=3600)
    def generate_schedule_c(self, user_id: int, year: int) -> Dict[str, Any]:
        """Generate Schedule C report"""
        try:
            cursor = self.db.cursor()
            # Add Schedule C specific queries here
            return {
                'schedule_c': {},
                'year': year,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            raise ReportGenerationError("Failed to generate Schedule C", 
                                        "schedule_c", {"error": str(e)})

    def generate_custom_report(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        categories: List[str] = None,
        report_type: str = 'detailed'
    ) -> Dict[str, Any]:
        """Generate custom report based on parameters"""
        try:
            cursor = self.db.cursor()
            query = """
                SELECT category, amount, date, description
                FROM expenses
                WHERE user_id = ?
                AND date BETWEEN ? AND ?
            """
            
            params = [user_id, start_date, end_date]
            
            if categories:
                query += " AND category IN ({})".format(
                    ','.join('?' * len(categories))
                )
                params.extend(categories)
                
            cursor.execute(query, params)
            expenses = cursor.fetchall()
            
            report_data = self._format_custom_report(expenses, report_type)
            self.cache.set_report_cache(user_id, 'custom_report', 
                                      {'start_date': start_date, 'end_date': end_date}, report_data)
            return report_data
        except Exception as e:
            raise ReportGenerationError("Failed to generate custom report", 
                                        "custom_report", {"error": str(e)})

    def _format_custom_report(
        self, 
        expenses: List[Dict], 
        report_type: str
    ) -> Dict[str, Any]:
        """Format the custom report based on type"""
        if report_type == 'summary':
            return self._generate_summary_format(expenses)
        return self._generate_detailed_format(expenses)
