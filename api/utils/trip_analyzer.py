from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .db_utils import Database

class TripAnalyzer:
    def __init__(self, database: Database):
        self.database = database
        self.logger = logging.getLogger(__name__)
        self.cache = {}

    def analyze_trip_patterns(self, user_id: int, 
                            date_range: Optional[tuple] = None) -> Dict[str, any]:
        """Analyze trip patterns for a user within a date range."""
        try:
            query = """
                SELECT start_location, end_location, distance, date
                FROM mileage
                WHERE user_id = ?
            """
            parameters = [user_id]

            if date_range:
                query += " AND date BETWEEN ? AND ?"
                parameters.extend(date_range)

            with self.database.get_cursor() as cursor:
                cursor.execute(query, parameters)
                trips = cursor.fetchall()

            if not trips:
                return {
                    'total_trips': 0,
                    'total_miles': 0,
                    'average_trip_length': 0,
                    'common_routes': [],
                    'peak_hours': {}
                }

            # Process trip data
            total_miles = sum(trip['distance'] for trip in trips)
            common_routes = self._analyze_common_routes(trips)
            peak_hours = self._analyze_peak_hours(trips)
            
            return {
                'total_trips': len(trips),
                'total_miles': round(total_miles, 2),
                'average_trip_length': round(total_miles / len(trips), 2),
                'common_routes': common_routes[:5],  # Top 5 common routes
                'peak_hours': peak_hours
            }

        except Exception as exception:
            self.logger.error(f"Error analyzing trip patterns: {str(exception)}")
            raise

    def get_cached_analysis(self, user_id: int, date_range: Optional[tuple] = None):
        """Get cached trip analysis if available"""
        cache_key = f"{user_id}_{date_range}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if cached_data['timestamp'] > datetime.now() - timedelta(hours=1):
                return cached_data['data']
        return None

    def _analyze_common_routes(self, trips: List[Dict]) -> List[Dict]:
        """Analyze most common routes from trip data."""
        route_counts = {}
        
        for trip in trips:
            route_key = f"{trip['start_location']} → {trip['end_location']}"
            if route_key in route_counts:
                route_counts[route_key]['count'] += 1
                route_counts[route_key]['total_distance'] += trip['distance']
            else:
                route_counts[route_key] = {
                    'count': 1,
                    'total_distance': trip['distance'],
                    'start': trip['start_location'],
                    'end': trip['end_location']
                }

        # Sort routes by frequency
        sorted_routes = sorted(
            route_counts.items(), 
            key=lambda x: (x[1]['count'], x[1]['total_distance']), 
            reverse=True
        )

        return [
            {
                'route': route,
                'frequency': data['count'],
                'total_distance': round(data['total_distance'], 2),
                'average_distance': round(data['total_distance'] / data['count'], 2)
            }
            for route, data in sorted_routes
        ]

    def _analyze_peak_hours(self, trips: List[Dict]) -> Dict[str, int]:
        """Analyze peak hours for trips."""
        hour_counts = {str(index).zfill(2): 0 for index in range(24)}
        
        for trip in trips:
            try:
                trip_hour = datetime.strptime(trip['date'], '%Y-%m-%d %H:%M:%S').hour
                hour_counts[str(trip_hour).zfill(2)] += 1
            except ValueError:
                self.logger.warning(f"Invalid date format in trip data: {trip['date']}")
                continue

        return dict(sorted(hour_counts.items(), key=lambda x: x[1], reverse=True))

    def get_earnings_per_mile(self, user_id: int, 
                            period: Optional[tuple] = None) -> Dict[str, float]:
        """Calculate earnings per mile for a given period."""
        try:
            # Get total earnings for the period
            earnings_query = """
                SELECT SUM(amount) as total_earnings
                FROM earnings
                WHERE user_id = ?
            """
            mileage_query = """
                SELECT SUM(distance) as total_miles
                FROM mileage
                WHERE user_id = ?
            """
            
            parameters = [user_id]
            if period:
                earnings_query += " AND date BETWEEN ? AND ?"
                mileage_query += " AND date BETWEEN ? AND ?"
                parameters.extend(period)

            with self.database.get_cursor() as cursor:
                cursor.execute(earnings_query, parameters)
                total_earnings = cursor.fetchone()['total_earnings'] or 0

                cursor.execute(mileage_query, parameters)
                total_miles = cursor.fetchone()['total_miles'] or 0

            return {
                'total_earnings': round(total_earnings, 2),
                'total_miles': round(total_miles, 2),
                'earnings_per_mile': round(
                    total_earnings / total_miles if total_miles > 0 else 0, 2
                )
            }

        except Exception as exception:
            self.logger.error(f"Error calculating earnings per mile: {str(exception)}")
            raise
