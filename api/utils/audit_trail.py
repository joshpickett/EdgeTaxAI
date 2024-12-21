import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from .db_utils import get_db_connection

class AuditTrail:
    def __init__(self):
        self.conn = get_db_connection()
        
    def log_category_change(self, 
                          expense_id: int, 
                          old_category: str, 
                          new_category: str,
                          user_id: int,
                          confidence_score: float) -> None:
        """Log category changes for audit purposes"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO category_changes 
                (expense_id, old_category, new_category, user_id, 
                 confidence_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                expense_id,
                old_category,
                new_category,
                user_id,
                confidence_score,
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error logging category change: {e}")
            
    def get_audit_trail(self, 
                       expense_id: Optional[int] = None, 
                       user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve audit trail for expenses"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM category_changes WHERE 1=1"
            params = []
            
            if expense_id:
                query += " AND expense_id = ?"
                params.append(expense_id)
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error retrieving audit trail: {e}")
            return []
