import logging
from typing import Dict, Any, List
import requests
from datetime import datetime

class GigPlatformProcessor:
    def __init__(self):
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
        
    def process_platform_data(self, platform: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw platform data into standardized format"""
        if platform == 'uber':
            return self._process_uber_data(raw_data)
        elif platform == 'lyft':
            return self._process_lyft_data(raw_data)
        elif platform == 'doordash':
            return self._process_doordash_data(raw_data)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
            
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
