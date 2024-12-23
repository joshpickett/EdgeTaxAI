from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from .db_utils import Database
from .analytics_helper import AnalyticsHelper
from .cache_utils import CacheManager

class AnalyticsIntegration:
    def __init__(self, db: Database):
        self.db = db
        self.analytics = AnalyticsHelper(db)
        self.cache = CacheManager()
        self.logger = logging.getLogger(__name__)

    def get_user_analytics(self, user_id: int, 
                         period: Optional[tuple] = None) -> Dict[str, any]:
        """Get cached or fresh analytics for a user."""
        cache_key = f"user_analytics:{user_id}:{period}"
        
        # Try to get from cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # Generate fresh analytics
            analytics_data = self.analytics.get_comprehensive_report(user_id, period)
            
            # Cache the results
            self.cache.set(cache_key, analytics_data, timeout=3600)  # Cache for 1 hour
            
            return analytics_data

        except Exception as e:
            self.logger.error(f"Error getting user analytics: {str(e)}")
            raise

    def refresh_analytics(self, user_id: int) -> None:
        """Force refresh analytics data for a user."""
        try:
            # Clear all cached analytics for this user
            cache_patterns = [
                f"user_analytics:{user_id}:*",
                f"earnings_summary:{user_id}:*",
                f"expense_analysis:{user_id}:*",
                f"trip_patterns:{user_id}:*"
            ]
            
            for pattern in cache_patterns:
                self.cache.delete(pattern)

            # Generate fresh analytics for different time periods
            periods = [
                ('daily', (datetime.now() - timedelta(days=1), datetime.now())),
                ('weekly', (datetime.now() - timedelta(weeks=1), datetime.now())),
                ('monthly', (datetime.now() - timedelta(days=30), datetime.now())),
                ('yearly', (datetime.now() - timedelta(days=365), datetime.now()))
            ]

            for period_name, period_range in periods:
                analytics_data = self.analytics.get_comprehensive_report(
                    user_id, period_range
                )
                cache_key = f"user_analytics:{user_id}:{period_name}"
                self.cache.set(cache_key, analytics_data, timeout=3600)

        except Exception as e:
            self.logger.error(f"Error refreshing analytics: {str(e)}")
            raise

    def get_platform_comparison(self, user_id: int, 
                              platforms: list) -> Dict[str, any]:
        """Compare earnings and metrics across different platforms."""
        try:
            platform_metrics = {}
            
            for platform in platforms:
                query = """
                    SELECT 
                        SUM(amount) as total_earnings,
                        COUNT(*) as trip_count,
                        AVG(amount) as avg_earnings
                    FROM earnings
                    WHERE user_id = ? AND platform = ?
                    AND date >= date('now', '-30 days')
                """
                
                with self.db.get_cursor() as cursor:
                    cursor.execute(query, (user_id, platform))
                    metrics = cursor.fetchone()
                    
                    platform_metrics[platform] = {
                        'total_earnings': round(metrics['total_earnings'] or 0, 2),
                        'trip_count': metrics['trip_count'] or 0,
                        'average_earnings': round(metrics['avg_earnings'] or 0, 2)
                    }

            return {
                'platform_metrics': platform_metrics,
                'top_platform': max(
                    platform_metrics.items(),
                    key=lambda x: x[1]['total_earnings']
                )[0] if platform_metrics else None,
                'comparison_period': '30 days'
            }

        except Exception as e:
            self.logger.error(f"Error comparing platforms: {str(e)}")
            raise

    def get_earnings_trends(self, user_id: int, 
                          period: str = 'weekly') -> Dict[str, any]:
        """Analyze earnings trends over time."""
        try:
            period_formats = {
                'daily': '%Y-%m-%d',
                'weekly': '%Y-%W',
                'monthly': '%Y-%m'
            }
            
            if period not in period_formats:
                raise ValueError(f"Invalid period: {period}")

            query = f"""
                SELECT 
                    strftime(?, date) as period,
                    SUM(amount) as total_earnings,
                    COUNT(*) as transaction_count
                FROM earnings
                WHERE user_id = ?
                GROUP BY period
                ORDER BY period DESC
                LIMIT 12
            """
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (period_formats[period], user_id))
                trends = cursor.fetchall()

            return {
                'period_type': period,
                'trends': [
                    {
                        'period': trend['period'],
                        'earnings': round(trend['total_earnings'], 2),
                        'transaction_count': trend['transaction_count'],
                        'average_per_transaction': round(
                            trend['total_earnings'] / trend['transaction_count'], 2
                        )
                    }
                    for trend in trends
                ],
                'total_periods': len(trends),
                'average_per_period': round(
                    sum(t['total_earnings'] for t in trends) / len(trends), 2
                ) if trends else 0
            }

        except Exception as e:
            self.logger.error(f"Error analyzing earnings trends: {str(e)}")
            raise
