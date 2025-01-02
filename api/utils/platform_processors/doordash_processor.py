from typing import Dict, Any, List
import logging
from datetime import datetime


class DoorDashProcessor:
    def __init__(self):
        self.platform = "doordash"

    async def process_trips(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process DoorDash delivery data"""
        try:
            processed_trips = []
            for delivery in raw_data.get("deliveries", []):
                processed_trip = {
                    "trip_id": delivery.get("delivery_id"),
                    "start_time": delivery.get("pickup_time"),
                    "end_time": delivery.get("delivery_time"),
                    "distance": delivery.get("total_distance"),
                    "duration": delivery.get("total_time"),
                    "earnings": delivery.get("earnings"),
                    "status": delivery.get("status"),
                    "platform": self.platform,
                }
                processed_trips.append(processed_trip)
            return processed_trips
        except Exception as e:
            logging.error(f"Error processing DoorDash deliveries: {e}")
            return []

    async def process_earnings(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process DoorDash earnings data"""
        try:
            return {
                "platform": self.platform,
                "period_start": raw_data.get("period_start"),
                "period_end": raw_data.get("period_end"),
                "gross_earnings": raw_data.get("total_earnings"),
                "expenses": raw_data.get("total_expenses", 0),
                "net_earnings": raw_data.get("net_earnings"),
                "deliveries_count": raw_data.get("total_deliveries", 0),
            }
        except Exception as e:
            logging.error(f"Error processing DoorDash earnings: {e}")
            return {}
