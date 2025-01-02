import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import asyncio
import logging
from typing import Callable, Any, Dict
from functools import wraps


class RetryHandler:
    def __init__(self, max_attempts: int = 3, initial_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay

    async def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry"""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = self.initial_delay * (2**attempt)
                    logging.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logging.error(f"All retry attempts failed: {str(e)}")

        raise last_exception


def with_retry(max_attempts: int = 3, initial_delay: float = 1.0):
    """Decorator for retry logic"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(max_attempts, initial_delay)
            return await retry_handler.retry_with_backoff(func, *args, **kwargs)

        return wrapper

    return decorator
