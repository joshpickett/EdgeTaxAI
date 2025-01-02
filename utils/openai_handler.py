from typing import Optional, Dict
import logging
from openai import OpenAI
from functools import wraps
from datetime import datetime, timedelta
from contextlib import contextmanager
import time


class TokenBucket:
    def __init__(self, tokens_per_min: int = 10000):
        self.tokens_per_min = tokens_per_min
        self.tokens = tokens_per_min
        self.last_update = datetime.now()

    def consume(self, tokens: int) -> bool:
        now = datetime.now()
        time_passed = now - self.last_update
        self.tokens = min(
            self.tokens_per_min,
            self.tokens + (time_passed.total_seconds() * self.tokens_per_min / 60),
        )
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class OpenAIHandler:
    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        tokens_per_min: int = 10000,
    ):
        self.client = OpenAI(api_key=api_key)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.token_bucket = TokenBucket(tokens_per_min)
        self.request_history: Dict[str, datetime] = {}

    def generate_completion(self, messages: list, model: str, **kwargs) -> dict:
        """Generate a completion with error handling."""
        retries = 0
        estimated_tokens = sum(len(m["content"].split()) * 1.3 for m in messages)

        while retries < self.max_retries:
            try:
                if not self.token_bucket.consume(int(estimated_tokens)):
                    delay = self._calculate_wait_time(estimated_tokens)
                    logging.info(
                        f"Rate limit approaching. Waiting {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                    continue

                response = self.client.chat.completions.create(
                    messages=messages, model=model, **kwargs
                )

                # Update request history
                now = datetime.now()
                self.request_history[now.isoformat()] = estimated_tokens
                self._cleanup_history()

                return response
            except Exception as e:
                retries += 1
                if retries >= self.max_retries:
                    raise
                delay = self.base_delay * (2**retries)
                logging.warning(
                    f"OpenAI API error: {str(e)}. Retrying in {delay} seconds..."
                )
                time.sleep(delay)
