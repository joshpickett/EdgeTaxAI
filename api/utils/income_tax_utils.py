from datetime import datetime
from typing import Dict, Tuple
from api.utils.db_utils import get_db_connection
from api.config import Config


class IncomeTaxCalculator:
    @staticmethod
    def get_quarterly_dates(quarter: int, year: int) -> Tuple[str, str]:
        """Get the start and end dates for a specific quarter"""
        quarter_dates = Config.QUARTERLY_TAX_DATES[quarter]
        start_date = f"{year}{quarter_dates['start']}"
        end_date = f"{year}{quarter_dates['end']}"

        return start_date, end_date

    @staticmethod
    def get_quarter_due_date(quarter: int, year: int) -> str:
        """Get the due date for a specific quarter"""
        due_date = Config.QUARTERLY_TAX_DATES[quarter]["due"]
        # Q4 is due in the next year
        if quarter == 4:
            year += 1
        return f"{year}{due_date}"

    @staticmethod
    def calculate_quarterly_amounts(user_id: int, quarter: int, year: int) -> Dict:
        """Calculate quarterly income and expenses for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()

        start_date, end_date = IncomeTaxCalculator.get_quarterly_dates(quarter, year)

        # Calculate total income
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total_income
            FROM income
            WHERE user_id = ? 
            AND date BETWEEN ? AND ?
        """,
            (user_id, start_date, end_date),
        )

        total_income = cursor.fetchone()[0]

        # Calculate total expenses
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total_expenses
            FROM expenses
            WHERE user_id = ?
            AND date BETWEEN ? AND ?
        """,
            (user_id, start_date, end_date),
        )

        total_expenses = cursor.fetchone()[0]

        conn.close()

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": total_income - total_expenses,
            "quarter": quarter,
            "year": year,
            "due_date": IncomeTaxCalculator.get_quarter_due_date(quarter, year),
        }
