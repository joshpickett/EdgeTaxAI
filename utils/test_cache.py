import json
import os
import hashlib
from typing import Optional, Dict
from datetime import datetime, timedelta


class TestCache:
    def __init__(self, cache_directory: str = ".test_cache"):
        self.cache_directory = cache_directory
        os.makedirs(cache_directory, exist_ok=True)
        self.cache_duration = timedelta(days=7)

    def _get_cache_key(self, code_content: str) -> str:
        return hashlib.md5(code_content.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        return os.path.join(self.cache_directory, f"{cache_key}.json")

    def get(self, code_content: str) -> Optional[str]:
        cache_key = self._get_cache_key(code_content)
        cache_path = self._get_cache_path(cache_key)

        if not os.path.exists(cache_path):
            return None

        with open(cache_path, "r") as file:
            cache_data = json.load(file)

        # Check if cache is expired
        cache_date = datetime.fromisoformat(cache_data["timestamp"])
        if datetime.now() - cache_date > self.cache_duration:
            os.remove(cache_path)
            return None

        return cache_data["test_content"]

    def set(self, code_content: str, test_content: str):
        cache_key = self._get_cache_key(code_content)
        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "test_content": test_content,
        }

        with open(cache_path, "w") as file:
            json.dump(cache_data, file)
