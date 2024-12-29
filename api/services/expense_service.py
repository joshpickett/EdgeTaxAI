import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from api.models.expenses import Expenses, ExpenseCategory
from api.config.database import SessionLocal
from datetime import datetime

class ExpenseService:
    def __init__(self):
        self.db = SessionLocal()

    def create_expense(self, data: Dict[str, Any]) -> Expenses:
        try:
            new_expense = Expenses(
                user_id=data['user_id'],
                category=data['category'],
                description=data['description'],
                amount=data['amount'],
                date=data['date']
            )
            self.db.add(new_expense)
            self.db.commit()
            return new_expense
        except Exception as e:
            self.db.rollback()
            raise e

    def get_expense(self, expense_id: int, user_id: int) -> Expenses:
        return self.db.query(Expenses).filter(
            Expenses.id == expense_id,
            Expenses.user_id == user_id
        ).first()

    def get_expenses_paginated(
        self, 
        user_id: int, 
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[int, List[Expenses]]:
        query = self.db.query(Expenses).filter(Expenses.user_id == user_id)
        total = query.count()
        expenses = query.offset((page - 1) * per_page).limit(per_page).all()
        return total, expenses
