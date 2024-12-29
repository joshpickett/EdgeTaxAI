import os
import sys
from api.setup_path import setup_python_path
from datetime import datetime
import logging
from typing import List, Dict, Any
from utils.db_utils import get_db_connection

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

class NotificationHandler:
    def __init__(self):
        self.db = get_db_connection()
        self.tax_deadlines = {
            'quarterly': [
                {'month': 4, 'day': 15},  # Q1
                {'month': 6, 'day': 15},  # Q2
                {'month': 9, 'day': 15},  # Q3
                {'month': 1, 'day': 15}   # Q4 (next year)
            ],
            'annual': [
                {'month': 4, 'day': 15}   # Annual tax deadline
            ]
        }
        
    def check_upcoming_deadlines(self, user_id: int) -> List[Dict[str, Any]]:
        """Check for upcoming tax deadlines"""
        try:
            current_date = datetime.now()
            upcoming_deadlines = []
            
            # Check quarterly deadlines
            for deadline in self.tax_deadlines['quarterly']:
                deadline_date = datetime(
                    current_date.year + (1 if deadline['month'] == 1 else 0),
                    deadline['month'],
                    deadline['day']
                )
                
                days_until = (deadline_date - current_date).days
                
                if 0 < days_until <= 30:  # Within 30 days
                    upcoming_deadlines.append({
                        'type': 'quarterly',
                        'due_date': deadline_date.isoformat(),
                        'days_remaining': days_until
                    })
            
            return upcoming_deadlines
            
        except Exception as e:
            logging.error(f"Error checking deadlines: {str(e)}")
            return []

...rest of the code...
