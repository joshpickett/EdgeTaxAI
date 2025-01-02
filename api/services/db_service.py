import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()


import sqlite3
import logging
from typing import Optional, Any
from contextlib import contextmanager


class DatabaseService:
    def __init__(self):
        self.database_file = os.getenv("DB_PATH", "database.db")

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.database_file)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> Any:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
