import os
import sys
from api.setup_path import setup_python_path

setup_python_path()

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from api.models.gig_platform import PlatformType, GigPlatformStatus
from api.utils.platform_processors.uber_processor import UberProcessor
from api.utils.platform_processors.lyft_processor import LyftProcessor
from api.utils.platform_processors.doordash_processor import DoorDashProcessor
from api.utils.platform_processors.instacart_processor import InstacartProcessor


class GigPlatformProcessor:
    def __init__(self):
        self.processors = {
            "uber": UberProcessor(),
            "lyft": LyftProcessor(),
            "doordash": DoorDashProcessor(),
            "instacart": InstacartProcessor(),
        }

    async def process_platform_data(
        self, platform: str, raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process platform-specific data"""
        try:
            processor = self.processors.get(platform.lower())
            if not processor:
                raise ValueError(f"Unsupported platform: {platform}")

            processed_data = await processor.process_trips(raw_data)
            return {
                "platform": platform,
                "trips": processed_data,
                "status": GigPlatformStatus.ACTIVE,
            }
        except Exception as e:
            logging.error(f"Error processing {platform} data: {e}")
            raise
