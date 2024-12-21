import logging
from typing import Dict, Any, List
from datetime import datetime

class TripAnalyzer:
    def __init__(self):
        self.business_keywords = [
            "client", "meeting", "delivery", "work",
            "business", "job site", "conference"
        ]
        
    def analyze_trip_purpose(self, purpose: str) -> Dict[str, Any]:
        """Analyze if a trip purpose is business-related"""
        purpose_lower = purpose.lower()
        business_score = sum(keyword in purpose_lower 
                           for keyword in self.business_keywords)
        
        is_business = business_score > 0
        suggestion = None if is_business else "Add business context to purpose"
        
        return {
            "is_business": is_business,
            "confidence": business_score / len(self.business_keywords),
            "suggestion": suggestion
        }
        
    def analyze_trip_pattern(self, trips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in trip data"""
        patterns = {
            "frequent_routes": self._analyze_frequent_routes(trips),
            "time_patterns": self._analyze_time_patterns(trips),
            "purpose_patterns": self._analyze_purpose_patterns(trips)
        }
        return patterns
        
    def _analyze_frequent_routes(self, trips: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze frequently traveled routes"""
        route_counts = {}
        for trip in trips:
            route = f"{trip['start']} -> {trip['end']}"
            route_counts[route] = route_counts.get(route, 0) + 1
        return route_counts
        
    def _analyze_time_patterns(self, trips: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze time patterns of trips"""
        morning_trips = []
        afternoon_trips = []
        evening_trips = []
        
        for trip in trips:
            trip_time = datetime.strptime(trip['date'], '%Y-%m-%d %H:%M:%S')
            hour = trip_time.hour
            
            if 5 <= hour < 12:
                morning_trips.append(trip['purpose'])
            elif 12 <= hour < 17:
                afternoon_trips.append(trip['purpose'])
            else:
                evening_trips.append(trip['purpose'])
                
        return {
            "morning": morning_trips,
            "afternoon": afternoon_trips,
            "evening": evening_trips
        }
        
    def _analyze_purpose_patterns(self, trips: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze patterns in trip purposes"""
        purpose_counts = {}
        for trip in trips:
            purpose = trip.get('purpose', 'unknown')
            purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
        return purpose_counts
