import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from api.models.gig_data_model import GigPlatform, GigTrip, PlatformType
from api.models.income import Income
from api.models.expenses import Expenses
from utils.gig_platform_processor import GigPlatformProcessor
from utils.gig_utils import PlatformAPI
from utils.sync_manager import SyncManager
from datetime import datetime
import logging

class GigPlatformService:
    def __init__(self, db: Session):
        self.db = db
        self.processor = GigPlatformProcessor()
        self.sync_manager = SyncManager()

    async def sync_platform_data(self, user_id: int, platform: str) -> Dict[str, Any]:
        try:
            # Get platform connection
            platform_conn = self.db.query(GigPlatform).filter(
                GigPlatform.user_id == user_id,
                GigPlatform.platform == PlatformType(platform)
            ).first()

            if not platform_conn:
                raise ValueError(f"No connected {platform} account found")

            # Fetch and process platform data
            api_client = PlatformAPI(platform, platform_conn.access_token)
            raw_data = await api_client.fetch_trips()
            processed_data = await self.processor.process_platform_data(platform, raw_data)

            # Process each trip
            for trip_data in processed_data["trips"]:
                # Check if trip already exists
                existing_trip = self.db.query(GigTrip).filter(
                    GigTrip.platform_id == platform_conn.id,
                    GigTrip.trip_id == trip_data["trip_id"]
                ).first()

                if existing_trip:
                    continue

                # Create trip record
                trip = GigTrip(
                    platform_id=platform_conn.id,
                    trip_id=trip_data["trip_id"],
                    start_time=trip_data["start_time"],
                    end_time=trip_data["end_time"],
                    earnings=trip_data["earnings"],
                    distance=trip_data["distance"],
                    status=trip_data["status"]
                )
                self.db.add(trip)

                # Create income record
                income = Income(
                    user_id=user_id,
                    platform_name=platform_conn.platform.value,
                    gross_income=trip_data["earnings"],
                    tips=trip_data.get("tips", 0),
                    platform_fees=trip_data.get("platform_fees", 0),
                    mileage=trip_data.get("distance", 0),
                    trip=trip
                )
                self.db.add(income)

                # Add any expenses
                if "expenses" in trip_data:
                    for expense_data in trip_data["expenses"]:
                        expense = Expenses(
                            user_id=user_id,
                            amount=expense_data["amount"],
                            description=expense_data["description"],
                            category=expense_data.get("category", "TRANSPORTATION"),
                            date=trip_data["start_time"].date(),
                            trip=trip
                        )
                        self.db.add(expense)

            self.db.commit()
            
            # Update sync status
            platform_conn.last_sync = datetime.utcnow()
            self.db.commit()
            
            # Trigger sync manager
            await self.sync_manager.sync_platform_data(user_id)

            return processed_data, 200

        except Exception as e:
            logging.error(f"Platform sync error: {e}")
            self.db.rollback()
            return {"error": str(e)}, 500

    def _get_access_token(self, user_id: int, platform: str) -> str:
        """Get platform access token from database"""
        # Implementation would fetch token from database
        pass
