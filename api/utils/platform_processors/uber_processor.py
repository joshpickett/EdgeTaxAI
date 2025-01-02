from typing import Dict, Any, List
import logging
from datetime import datetime


class UberProcessor:
    def __init__(self):
        self.platform = "uber"

    async def process_trips(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Uber trip data"""
        try:
            processed_trips = []
            for trip in raw_data.get("trips", []):
                processed_trip = {
                    "trip_id": trip.get("uuid"),
                    "start_time": trip.get("pickup_time"),
                    "end_time": trip.get("dropoff_time"),
                    "distance": trip.get("distance"),
                    "duration": trip.get("duration"),
                    "earnings": trip.get("fare_amount"),
                    "status": trip.get("status"),
                    "platform": self.platform,
                }
                processed_trips.append(processed_trip)
            return processed_trips
        except Exception as e:
            logging.error(f"Error processing Uber trips: {e}")
            return []

    async def process_earnings(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Uber earnings data"""
        try:
            return {
                "platform": self.platform,
                "period_start": raw_data.get("period_start"),
                "period_end": raw_data.get("period_end"),
                "gross_earnings": raw_data.get("earnings_total"),
                "expenses": raw_data.get("expenses_total", 0),
                "net_earnings": raw_data.get("net_earnings"),
                "trips_count": raw_data.get("trips_count", 0),
            }
        except Exception as e:
            logging.error(f"Error processing Uber earnings: {e}")
            return {}
