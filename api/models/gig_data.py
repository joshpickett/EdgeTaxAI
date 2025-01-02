# deprecated not used

import sqlite3
import logging
from typing import Dict, Any, Optional
from datetime import datetime


class GigData:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path

    def init_tables(self):
        """Initialize gig data tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gig_trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                trip_id TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                earnings REAL,
                distance REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, trip_id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gig_earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                period_start DATE,
                period_end DATE,
                gross_earnings REAL,
                expenses REAL,
                net_earnings REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gig_sync_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                last_sync TIMESTAMP,
                sync_status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, platform)
            )
        """
        )

        conn.commit()
        conn.close()

    def store_trip(self, trip_data: Dict[str, Any]) -> Optional[int]:
        """Store trip data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO gig_trips (
                    user_id, platform, trip_id, start_time,
                    end_time, earnings, distance, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    trip_data["user_id"],
                    trip_data["platform"],
                    trip_data["trip_id"],
                    trip_data["start_time"],
                    trip_data["end_time"],
                    trip_data["earnings"],
                    trip_data["distance"],
                    trip_data["status"],
                ),
            )

            trip_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return trip_id
        except Exception as e:
            logging.error(f"Error storing trip: {e}")
            return None

    def store_earnings(self, earnings_data: Dict[str, Any]) -> Optional[int]:
        """Store earnings data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO gig_earnings (
                    user_id, platform, period_start, period_end,
                    gross_earnings, expenses, net_earnings
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    earnings_data["user_id"],
                    earnings_data["platform"],
                    earnings_data["period_start"],
                    earnings_data["period_end"],
                    earnings_data["gross_earnings"],
                    earnings_data["expenses"],
                    earnings_data["net_earnings"],
                ),
            )

            earnings_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return earnings_id
        except Exception as e:
            logging.error(f"Error storing earnings: {e}")
            return None

    def update_sync_status(
        self, user_id: int, platform: str, status: str, error: str = None
    ) -> bool:
        """Update platform sync status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO gig_sync_status (user_id, platform, last_sync, sync_status, error_message)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
                ON CONFLICT(user_id, platform) 
                DO UPDATE SET 
                    last_sync=CURRENT_TIMESTAMP,
                    sync_status=excluded.sync_status,
                    error_message=excluded.error_message
            """,
                (user_id, platform, status, error),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating sync status: {e}")
            return False
