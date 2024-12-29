from typing import Dict, Any, List
import logging
from datetime import datetime

class InstacartProcessor:
    def __init__(self):
        self.platform = "instacart"
        
    async def process_trips(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Instacart delivery data"""
        try:
            processed_trips = []
            for delivery in raw_data.get('deliveries', []):
                processed_trip = {
                    'trip_id': delivery.get('batch_id'),
                    'start_time': delivery.get('start_time'),
                    'end_time': delivery.get('completion_time'),
                    'distance': delivery.get('total_distance'),
                    'duration': delivery.get('total_time'),
                    'earnings': delivery.get('batch_earnings'),
                    'tips': delivery.get('customer_tip'),
                    'status': delivery.get('status'),
                    'platform': self.platform
                }
                processed_trips.append(processed_trip)
            return processed_trips
        except Exception as e:
            logging.error(f"Error processing Instacart deliveries: {e}")
            return []
            
    async def process_earnings(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Instacart earnings data"""
        try:
            return {
                'platform': self.platform,
                'period_start': raw_data.get('period_start'),
                'period_end': raw_data.get('period_end'),
                'gross_earnings': raw_data.get('total_earnings'),
                'batch_earnings': raw_data.get('batch_earnings'),
                'tips': raw_data.get('total_tips'),
                'adjustments': raw_data.get('adjustments', 0),
                'net_earnings': raw_data.get('net_earnings'),
                'deliveries_count': raw_data.get('total_batches', 0)
            }
        except Exception as e:
            logging.error(f"Error processing Instacart earnings: {e}")
            return {}
