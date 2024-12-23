from typing import Optional
import logging
from openai import OpenAI
from functools import wraps
from contextlib import contextmanager
import time

class OpenAIHandler:
    def __init__(self, api_key: str, max_retries: int = 3, base_delay: float = 1.0):
        self.client = OpenAI(api_key=api_key)
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    def generate_completion(self, messages: list, **kwargs) -> dict:
        """Generate a completion with error handling."""
        retries = 0
        while retries < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    **kwargs
                )
                return response
            except Exception as e:
                retries += 1
                if retries >= self.max_retries:
                    raise
                delay = self.base_delay * (2 ** retries)
                logging.warning(f"OpenAI API error: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
