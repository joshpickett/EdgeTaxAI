import logging
from typing import Dict, List, Any
from datetime import datetime
from .db_utils import get_db_connection
from .error_handler import handle_sync_error

class SyncManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = get_db_connection()

    async def sync_user_data(self, user_id: str) -> Dict[str, Any]:
        """Synchronize all user data"""
        try:
            sync_result = {
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat(),
                'synced_items': {}
            }

            # Sync different data types
            sync_result['synced_items']['expenses'] = await self.sync_expenses(user_id)
            sync_result['synced_items']['receipts'] = await self.sync_receipts(user_id)
            sync_result['synced_items']['platform_data'] = await self.sync_platform_data(user_id)

            return sync_result

        except Exception as e:
            self.logger.error(f"Sync error for user {user_id}: {str(e)}")
            return handle_sync_error(e)

    async def sync_expenses(self, user_id: str) -> Dict[str, Any]:
        """Sync user expenses"""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM expenses WHERE user_id = ? AND sync_status = 'pending'",
                (user_id,)
            )
            pending_expenses = cursor.fetchall()

            synced_count = 0
            for expense in pending_expenses:
                # Process each expense
                await self._process_expense_sync(expense)
                synced_count += 1

            return {
                'status': 'success',
                'synced_count': synced_count
            }

        except Exception as e:
            self.logger.error(f"Error syncing expenses: {str(e)}")
            raise

    async def sync_receipts(self, user_id: str) -> Dict[str, Any]:
        """Sync user receipts"""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM receipts WHERE user_id = ? AND sync_status = 'pending'",
                (user_id,)
            )
            pending_receipts = cursor.fetchall()

            synced_count = 0
            for receipt in pending_receipts:
                await self._process_receipt_sync(receipt)
                synced_count += 1

            return {
                'status': 'success',
                'synced_count': synced_count
            }

        except Exception as e:
            self.logger.error(f"Error syncing receipts: {str(e)}")
            raise

    async def sync_platform_data(self, user_id: str) -> Dict[str, Any]:
        """Sync platform-specific data"""
        try:
            platforms = ['uber', 'lyft', 'doordash', 'instacart']
            platform_results = {}

            for platform in platforms:
                platform_results[platform] = await self._sync_platform(user_id, platform)

            return {
                'status': 'success',
                'platform_results': platform_results
            }

        except Exception as e:
            self.logger.error(f"Error syncing platform data: {str(e)}")
            raise

    async def _process_expense_sync(self, expense: Dict[str, Any]) -> None:
        """Process individual expense sync"""
        try:
            # Update sync status
            cursor = self.db.cursor()
            cursor.execute(
                "UPDATE expenses SET sync_status = 'synced', last_synced = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), expense['id'])
            )
            self.db.commit()

        except Exception as e:
            self.logger.error(f"Error processing expense sync: {str(e)}")
            raise

    async def _process_receipt_sync(self, receipt: Dict[str, Any]) -> None:
        """Process individual receipt sync"""
        try:
            # Update sync status
            cursor = self.db.cursor()
            cursor.execute(
                "UPDATE receipts SET sync_status = 'synced', last_synced = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), receipt['id'])
            )
            self.db.commit()

        except Exception as e:
            self.logger.error(f"Error processing receipt sync: {str(e)}")
            raise

    async def _sync_platform(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Sync data for specific platform"""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM platform_data WHERE user_id = ? AND platform = ? AND sync_status = 'pending'",
                (user_id, platform)
            )
            pending_data = cursor.fetchall()

            synced_count = 0
            for data in pending_data:
                # Process platform-specific data
                await self._process_platform_data_sync(data)
                synced_count += 1

            return {
                'status': 'success',
                'synced_count': synced_count
            }

        except Exception as e:
            self.logger.error(f"Error syncing platform {platform}: {str(e)}")
            raise

    async def _process_platform_data_sync(self, data: Dict[str, Any]) -> None:
        """Process platform-specific data sync"""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "UPDATE platform_data SET sync_status = 'synced', last_synced = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), data['id'])
            )
            self.db.commit()

        except Exception as e:
            self.logger.error(f"Error processing platform data sync: {str(e)}")
            raise
