import os
import requests
from typing import Dict, Tuple, Optional
from api.config import TAX_CONFIG
from api.utils.cache_utils import CacheManager
from api.utils.error_handler import APIError

class TripAnalyzer:
    def __init__(self):
        self.cache = CacheManager()
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    def calculate_trip_distance(self, start: str, end: str) -> Tuple[float, Optional[str]]:
        """Calculate distance between two points using Google Maps API"""
        cache_key = f"distance:{start}:{end}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return cached_result, None
            
        try:
            url = f"https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': start,
                'destination': end,
                'key': self.google_maps_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                return 0, f"API Error: {data['status']}"
                
            distance = data['routes'][0]['legs'][0]['distance']['value'] / 1609.34  # Convert meters to miles
            self.cache.set(cache_key, distance, timeout=86400)  # Cache for 24 hours
            
            return distance, None
            
        except Exception as e:
            return 0, str(e)

...rest of the code...
