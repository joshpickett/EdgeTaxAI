from typing import Dict, Any, List
import logging
from datetime import datetime


class LyftProcessor:
    def __init__(self):
        self.platform = "lyft"

    async def process_trips(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Lyft trip data"""
        try:
            processed_trips = []
            for ride in raw_data.get("rides", []):
                processed_trip = {
                    "trip_id": ride.get("ride_id"),
                    "start_time": ride.get("started_at"),
                    "end_time": ride.get("ended_at"),
                    "distance": ride.get("distance_miles"),
                    "duration": ride.get("duration_seconds"),
                    "earnings": ride.get("earnings"),
                    "status": ride.get("status"),
                    "platform": self.platform,
                }
                processed_trips.append(processed_trip)
            return processed_trips
        except Exception as e:
            logging.error(f"Error processing Lyft trips: {e}")
            return []

    async def process_earnings(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Lyft earnings data"""
        try:
            return {
                "platform": self.platform,
                "period_start": raw_data.get("start_date"),
                "period_end": raw_data.get("end_date"),
                "gross_earnings": raw_data.get("total_earnings"),
                "expenses": raw_data.get("total_expenses", 0),
                "net_earnings": raw_data.get("net_earnings"),
                "rides_count": raw_data.get("total_rides", 0),
            }
        except Exception as e:
            logging.error(f"Error processing Lyft earnings: {e}")
            return {}
