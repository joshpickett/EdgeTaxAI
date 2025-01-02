from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


class ErrorMetricsCollector:
    """Service for collecting and analyzing error metrics"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts = defaultdict(int)
        self.error_history = defaultdict(list)
        self.retention_days = 7

    async def collect_error(self, error: Exception, error_type: str) -> None:
        """Collect error metrics"""
        try:
            error_key = type(error).__name__
            self.error_counts[error_key] += 1

            self.error_history[error_key].append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": error_type,
                    "message": str(error),
                }
            )

            # Cleanup old entries
            await self._cleanup_old_entries()

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")

    async def get_frequency(self, error_type: str) -> Dict[str, Any]:
        """Get error frequency statistics"""
        try:
            now = datetime.utcnow()
            history = self.error_history[error_type]

            # Calculate frequencies
            last_hour = len(
                [
                    e
                    for e in history
                    if datetime.fromisoformat(e["timestamp"]) > now - timedelta(hours=1)
                ]
            )

            last_day = len(
                [
                    e
                    for e in history
                    if datetime.fromisoformat(e["timestamp"]) > now - timedelta(days=1)
                ]
            )

            return {
                "total_count": self.error_counts[error_type],
                "last_hour": last_hour,
                "last_day": last_day,
                "trend": self._calculate_trend(error_type),
            }

        except Exception as e:
            self.logger.error(f"Error getting frequency: {str(e)}")
            return {"total_count": 0, "last_hour": 0, "last_day": 0, "trend": "stable"}

    def _calculate_trend(self, error_type: str) -> str:
        """Calculate error frequency trend"""
        try:
            history = self.error_history[error_type]
            if len(history) < 2:
                return "stable"

            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            two_hours_ago = now - timedelta(hours=2)

            recent_count = len(
                [
                    e
                    for e in history
                    if datetime.fromisoformat(e["timestamp"]) > hour_ago
                ]
            )

            previous_count = len(
                [
                    e
                    for e in history
                    if hour_ago > datetime.fromisoformat(e["timestamp"]) > two_hours_ago
                ]
            )

            if recent_count > previous_count * 1.5:
                return "increasing"
            elif recent_count < previous_count * 0.5:
                return "decreasing"
            return "stable"

        except Exception as e:
            self.logger.error(f"Error calculating trend: {str(e)}")
            return "stable"

    async def _cleanup_old_entries(self) -> None:
        """Clean up old error history entries"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=self.retention_days)

            for error_type in self.error_history:
                self.error_history[error_type] = [
                    entry
                    for entry in self.error_history[error_type]
                    if datetime.fromisoformat(entry["timestamp"]) > cutoff
                ]

        except Exception as e:
            self.logger.error(f"Error cleaning up entries: {str(e)}")
