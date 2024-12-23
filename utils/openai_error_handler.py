from typing import Optional, Callable
import time
import logging
from openai import APIError, RateLimitError, APITimeoutError
from functools import wraps

def handle_openai_errors(max_retries: int = 3, base_delay: float = 1.0) -> Callable:
    """
    Decorator to handle OpenAI API errors with exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay for exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if retries == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** retries)
                    logging.warning(f"Rate limit hit, retrying in {delay} seconds...")
                    time.sleep(delay)
                except APITimeoutError as e:
                    if retries == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** retries)
                    logging.warning(f"Timeout error, retrying in {delay} seconds...")
                    time.sleep(delay)
                except APIError as e:
                    if retries == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** retries)
                    logging.warning(f"API error occurred, retrying in {delay} seconds...")
                    time.sleep(delay)
                retries += 1
            return None
        return wrapper
    return decorator
