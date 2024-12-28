from desktop.setup_path import setup_desktop_path
setup_desktop_path()

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class SyncManager:
    def __init__(self, database_path: str = "expenses.db"):
        self.database_path = database_path
        self.setup_database()

    def setup_database(self):
        """Setup sync-related database tables"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            # Create sync status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_status (
                    id INTEGER PRIMARY KEY,
                    last_sync TIMESTAMP,
                    status TEXT,
                    details TEXT
                )
            """)
            
            # Create offline queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS offline_queue (
                    id INTEGER PRIMARY KEY,
                    operation TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
        except Exception as exception:
            logging.error(f"Database setup error: {exception}")
        finally:
            connection.close()

    async def get_local_expenses(self) -> List[Dict[str, Any]]:
        """Get all local expenses that need syncing"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT * FROM expenses 
                WHERE synced = 0 OR modified_at > last_synced_at
            """)
            
            expenses = cursor.fetchall()
            return [self._row_to_dict(expense) for expense in expenses]
        except Exception as exception:
            logging.error(f"Error getting local expenses: {exception}")
            return []
        finally:
            connection.close()

    async def queue_offline_operation(self, operation: str, data: Dict[str, Any]):
        """Queue an operation for later sync"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            cursor.execute(
                "INSERT INTO offline_queue (operation, data) VALUES (?, ?)",
                (operation, json.dumps(data))
            )
            
            connection.commit()
        except Exception as exception:
            logging.error(f"Error queuing operation: {exception}")
        finally:
            connection.close()

    async def update_sync_status(self, status: str, details: str = None):
        """Update the sync status"""
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()
            
            cursor.execute(
                """INSERT OR REPLACE INTO sync_status 
                   (id, last_sync, status, details) VALUES (1, ?, ?, ?)""",
                (datetime.now().isoformat(), status, details)
            )
            
            connection.commit()
        except Exception as exception:
            logging.error(f"Error updating sync status: {exception}")
        finally:
            connection.close()

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert a database row to a dictionary"""
        return {
            "id": row[0],
            "description": row[1],
            "amount": row[2],
            "category": row[3],
            "date": row[4],
            "synced": row[5],
            "modified_at": row[6]
        }
