import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
from .cache_utils import CacheManager
from .error_handler import handle_api_error
from .retry_handler import with_retry
from .platform_processors.uber_processor import UberProcessor
from .platform_processors.lyft_processor import LyftProcessor
from .platform_processors.doordash_processor import DoorDashProcessor

PROCESSORS = {
    'uber': UberProcessor(),
    'lyft': LyftProcessor(),
    'doordash': DoorDashProcessor()
}

class GigPlatformProcessor:
    def __init__(self):
        self.cache = CacheManager()
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
            processor = PROCESSORS.get(platform)
            if not processor:
                raise ValueError(f"No processor found for {platform}")

            trips = await processor.process_trips(raw_data)
            earnings = await processor.process_earnings(raw_data)
             
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
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            
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
