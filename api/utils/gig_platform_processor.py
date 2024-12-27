import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import sqlite3
from api.utils.cache_utils import CacheManager
from api.utils.error_handler import handle_api_error
from api.utils.retry_handler import with_retry
from api.utils.platform_processors.uber_processor import UberProcessor
from api.utils.platform_processors.lyft_processor import LyftProcessor
from api.utils.platform_processors.doordash_processor import DoorDashProcessor

PROCESSORS = {
    'uber': UberProcessor(),
    'lyft': LyftProcessor(),
    'doordash': DoorDashProcessor()
}

class GigPlatformProcessor:
    def __init__(self):
        self.cache = CacheManager()
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "..", "database.db"))
        self.retry_attempts = 3
        self.sync_queue = asyncio.Queue()
        self.processing = False

    async def start_sync_worker(self):
        """Start background sync worker"""
        self.processing = True
        while self.processing:
            try:
                sync_task = await self.sync_queue.get()
                await self._process_sync_task(sync_task)
            except Exception as e:
                logging.error(f"Sync worker error: {e}")
            finally:
                self.sync_queue.task_done()

    async def stop_sync_worker(self):
        """Stop background sync worker"""
        self.processing = False
        await self.sync_queue.join()
        logging.info("Sync worker stopped")

        self.platforms = {
            'uber': {
                'expense_categories': {
                    'rides': 'transportation',
                    'deliveries': 'delivery_expenses'
                }
            },
            'lyft': {
                'expense_categories': {
                    'rides': 'transportation'
                }
            },
            'doordash': {
                'expense_categories': {
                    'deliveries': 'delivery_expenses',
                    'supplies': 'equipment'
                }
            }
        }

    @with_retry(max_attempts=3, initial_delay=1.0)
    async def process_platform_data(self, platform: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw platform data into standardized format"""
        try:
            # Get platform processor
            processor = self._get_processor(platform)
            if not processor:
                raise ValueError(f"No processor found for {platform}")

            # Process data with retries
            trips = await self._process_with_retry(
                processor.process_trips,
                raw_data
            )
            
            earnings = await self._process_with_retry(
                processor.process_earnings,
                raw_data
            )
            
            # Create expense entries for trips
            await self._create_expense_entries(trips, platform)
            
            # Store income data
            await self._store_income_data(earnings, platform)

            # Validate processed data
            self._validate_processed_data(trips, earnings)
            
            # Store sync status
            await self._update_sync_status(
                platform,
                'success',
                datetime.now().isoformat()
            )
            
            # Cache processed data
            await self.cache.set_platform_data(
                platform,
                {'trips': trips, 'earnings': earnings}
            )

            processed_data = {
                'trips': trips,
                'earnings': earnings,
                'platform': platform,
                'processed_at': datetime.now().isoformat()
            }

            return processed_data
        except Exception as e:
            logging.error(f"Error processing platform data: {e}")
            raise
            
    def _process_uber_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Uber specific data"""
        trips = data.get('trips', [])
        processed_data = {
            'earnings': sum(trip.get('earnings', 0) for trip in trips),
            'expenses': self._categorize_uber_expenses(trips),
            'mileage': sum(trip.get('distance', 0) for trip in trips),
            'period': {
                'start': min(trip.get('start_time') for trip in trips),
                'end': max(trip.get('end_time') for trip in trips)
            }
        }
        return processed_data
        
    def _process_lyft_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Lyft specific data"""
        rides = data.get('rides', [])
        processed_data = {
            'earnings': sum(ride.get('earnings', 0) for ride in rides),
            'expenses': self._categorize_lyft_expenses(rides),
            'mileage': sum(ride.get('distance', 0) for ride in rides),
            'period': {
                'start': min(ride.get('start_time') for ride in rides),
                'end': max(ride.get('end_time') for ride in rides)
            }
        }
        return processed_data
        
    def _categorize_uber_expenses(self, trips: List[Dict[str, Any]]) -> Dict[str, float]:
        """Categorize Uber expenses"""
        categories = {}
        for trip in trips:
            category = self.platforms['uber']['expense_categories'].get(
                trip.get('type', 'rides'),
                'other'
            )
            if category not in categories:
                categories[category] = 0
            categories[category] += trip.get('expenses', 0)
        return categories
        
    def _categorize_lyft_expenses(self, rides: List[Dict[str, Any]]) -> Dict[str, float]:
        """Categorize Lyft expenses"""
        categories = {}
        for ride in rides:
            category = self.platforms['lyft']['expense_categories'].get(
                ride.get('type', 'rides'),
                'other'
            )
            if category not in categories:
                categories[category] = 0
            categories[category] += ride.get('expenses', 0)
        return categories

    @with_retry(max_attempts=3, initial_delay=2.0)
    async def auto_sync_platforms(self):
        """Auto-sync platform data based on configured intervals"""
        try:
            cursor = self.conn.cursor()
            
            # Get platforms due for sync
            cursor.execute("""
                SELECT user_id, platform, last_sync 
                FROM gig_sync_status
                WHERE sync_status != 'in_progress'
            """)
            
            platforms = cursor.fetchall()
            for user_id, platform, last_sync in platforms:
                try:
                    # Check if sync is needed based on last sync time
                    if self._should_sync(last_sync):
                        await self._perform_sync(user_id, platform)
                except Exception as e:
                    logging.error(f"Error syncing {platform} for user {user_id}: {e}")
                    
        except Exception as e:
            logging.error(f"Error in auto sync: {e}")
            return False

    async def retry_failed_sync(self, user_id: int, platform: str) -> bool:
        """Retry failed platform sync with exponential backoff"""
        for attempt in range(self.retry_attempts):
            try:
                backoff_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(backoff_time)
                
                if await self._perform_sync(user_id, platform):
                    logging.info(f"Sync succeeded on attempt {attempt + 1}")
                    return True
                    
            except Exception as e:
                logging.error(f"Sync attempt {attempt + 1} failed: {e}")
                
        return False

    def _handle_sync_error(self, user_id: int, platform: str, error: Exception) -> None:
        """Handle sync errors and update status"""
        try:
            error_message = str(error)
            self._update_sync_status(user_id, platform, "failed", error_message)
            logging.error(f"Sync error for {platform}: {error_message}")
        except Exception as e:
            logging.error(f"Error handling sync error: {e}")

    def _should_sync(self, last_sync: str) -> bool:
        """Determine if sync is needed based on last sync time"""
        if not last_sync:
            return True
            
        last_sync_time = datetime.fromisoformat(last_sync)
        sync_interval = timedelta(hours=24)  # Default 24 hour interval
        
        return datetime.now() - last_sync_time > sync_interval

    async def _process_with_retry(self, processor_function, data):
        """Process data with retry logic"""
        retries = 3
        for attempt in range(retries):
            try:
                return await processor_function(data)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def _create_expense_entries(self, trips: List[Dict[str, Any]], platform: str) -> None:
        """Create expense entries for trips"""
        try:
            cursor = self.conn.cursor()
            for trip in trips:
                cursor.execute("""
                    INSERT INTO expenses (
                        description, amount, category, platform_source, 
                        platform_trip_id, tax_deductible
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    trip.get('description'),
                    trip.get('expenses', 0),
                    self.platforms[platform]['expense_categories'].get(trip.get('type', 'rides'), 'other'),
                    platform,
                    trip.get('id'),
                    True
                ))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error creating expense entries: {e}")
            raise

    async def _store_income_data(self, earnings: Dict[str, Any], platform: str) -> None:
        """Store income data in the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO income (
                    user_id, platform, amount, period_start, period_end, type
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                earnings['user_id'],
                platform,
                earnings['gross_earnings'],
                earnings['period_start'],
                earnings['period_end'],
                'gig_platform'
            ))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error storing income data: {e}")
            raise

    def _validate_processed_data(self, trips, earnings):
        """Validate processed platform data"""
        if not isinstance(trips, list):
            raise ValueError("Trips must be a list")
        if not isinstance(earnings, dict):
            raise ValueError("Earnings must be a dictionary")
        if not all(isinstance(t, dict) for t in trips):
            raise ValueError("All trips must be dictionaries")
        if not all(k in earnings for k in ['gross_earnings', 'net_earnings']):
            raise ValueError("Missing required earnings fields")
