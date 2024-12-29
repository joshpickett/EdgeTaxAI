import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
from api.models.gig_platform import GigPlatform, GigTrip, GigEarnings, PlatformType, GigPlatformStatus
from api.schemas.gig_schemas import GigPlatformCreate, GigTripCreate
from api.models.income import Income
from api.models.expenses import Expenses
from utils.gig_platform_processor import GigPlatformProcessor
from utils.gig_utils import PlatformAPI
from utils.sync_manager import SyncManager
from datetime import datetime
from api.utils.encryption_utils import EncryptionManager
import logging

class GigPlatformService:
    def __init__(self, db: Session):
        self.db = db
        self.processor = GigPlatformProcessor()
        self.encryption_manager = EncryptionManager()
        self.sync_manager = SyncManager()

    def create_platform(self, user_id: int, platform_data: GigPlatformCreate) -> GigPlatform:
        """Create a new platform connection"""
        try:
            platform = GigPlatform(
                user_id=user_id,
                platform=platform_data.platform,
                platform_user_id=platform_data.platform_user_id,
                platform_email=platform_data.platform_email,
                access_token=platform_data.access_token,
                refresh_token=platform_data.refresh_token,
                account_status=GigPlatformStatus.PENDING,
                metadata=platform_data.metadata
            )

            self.db.add(platform)
            self.db.commit()
            self.db.refresh(platform)
            return platform
        except Exception as e:
            self.db.rollback()
            raise e

    async def sync_platform_data(self, platform_id: int) -> Dict[str, Any]:
        """Sync platform data and create/update records"""
        try:
            platform = self.db.query(GigPlatform).filter(
                GigPlatform.id == platform_id,
                GigPlatform.is_active == True
            ).first()
             
            if not platform:
                raise ValueError("Platform connection not found")
 
            api_client = PlatformAPI(
                platform=platform.platform,
                access_token=platform.decrypted_access_token
            )

            # Fetch and process platform data
            raw_data = await api_client.fetch_trips()
            processed_data = await self.processor.process_platform_data(platform.platform, raw_data)

            # Process each trip
            for trip_data in processed_data["trips"]:
                # Check if trip already exists
                existing_trip = self.db.query(GigTrip).filter(
                    GigTrip.platform_id == platform.id,
                    GigTrip.trip_id == trip_data["trip_id"]
                ).first()

                if existing_trip:
                    continue

                # Create trip record
                trip = GigTrip(
                    platform_id=platform.id,
                    trip_id=trip_data["trip_id"],
                    start_time=trip_data["start_time"],
                    end_time=trip_data["end_time"],
                    earnings=trip_data["earnings"],
                    distance=trip_data["distance"],
                    status=trip_data["status"],
                    base_fare=trip_data.get("base_fare"),
                    tips=trip_data.get("tips"),
                    bonuses=trip_data.get("bonuses"),
                    metadata=trip_data.get("metadata")
                )
                self.db.add(trip)

                # Create income record
                income = Income(
                    user_id=platform.user_id,
                    platform_name=platform.platform.value,
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
                            user_id=platform.user_id,
                            amount=expense_data["amount"],
                            description=expense_data["description"],
                            category=expense_data.get("category", "TRANSPORTATION"),
                            date=trip_data["start_time"].date(),
                            trip=trip
                        )
                        self.db.add(expense)

            # Create earnings summary
            earnings_summary = GigEarnings(
                platform_id=platform.id,
                period_start=min(t["start_time"] for t in processed_data["trips"]),
                period_end=max(t["end_time"] for t in processed_data["trips"]),
                gross_earnings=sum(t["earnings"] for t in processed_data["trips"]),
                net_earnings=sum(t["earnings"] - t.get("platform_fees", 0) for t in processed_data["trips"]),
                trips_count=len(processed_data["trips"]),
                metadata={"sync_date": datetime.utcnow().isoformat()}
            )
            self.db.add(earnings_summary)

            platform.last_sync = datetime.utcnow()
            platform.account_status = GigPlatformStatus.ACTIVE
            self.db.commit()
            
            # Trigger sync manager
            await self.sync_manager.sync_platform_data(platform.user_id)

            return processed_data

        except Exception as e:
            logging.error(f"Platform sync error: {e}")
            self.db.rollback()
            return {"error": str(e)}, 500

    def _get_access_token(self, user_id: int, platform: str) -> str:
        """Get platform access token from database"""
        # Implementation would fetch token from database
        pass

    async def create_earnings(self, earnings_data: GigEarningsCreate) -> GigEarnings:
        """Create earnings record"""
        try:
            earnings = GigEarnings(
                platform_id=earnings_data.platform_id,
                period_start=earnings_data.period_start,
                period_end=earnings_data.period_end,
                gross_earnings=earnings_data.gross_earnings,
                net_earnings=earnings_data.net_earnings,
                trips_count=earnings_data.trips_count,
                metadata=earnings_data.metadata
            )
            self.db.add(earnings)
            self.db.commit()
            self.db.refresh(earnings)
            return earnings
        except Exception as e:
            self.db.rollback()
            raise e
