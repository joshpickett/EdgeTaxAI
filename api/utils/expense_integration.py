import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from api.utils.db_utils import get_db_connection


class ExpenseIntegration:
    def __init__(self):
        self.conn = get_db_connection()

    def create_expense_entry(self, data: Dict[str, Any], user_id: str) -> Optional[int]:
        """Create a new expense entry from Optical Character Recognition data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (
                    user_id, description, amount, category, 
                    date, receipt_url, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    data.get("description", "Receipt Expense"),
                    data.get("amount", 0.0),
                    data.get("category", "Uncategorized"),
                    data.get("date", datetime.now().strftime("%Y-%m-%d")),
                    data.get("receipt_url", ""),
                    data.get("confidence_score", 0.0),
                ),
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error creating expense entry: {e}")
            return None

    def update_expense_entry(self, expense_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing expense entry"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE expenses 
                SET description=?, amount=?, category=?, 
                    date=?, receipt_url=?, confidence_score=?
                WHERE id=?
            """,
                (
                    data.get("description"),
                    data.get("amount"),
                    data.get("category"),
                    data.get("date"),
                    data.get("receipt_url"),
                    data.get("confidence_score"),
                    expense_id,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating expense entry: {e}")
            return False
