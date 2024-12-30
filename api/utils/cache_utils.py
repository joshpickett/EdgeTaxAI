class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.default_timeout = 3600
        self.compression_threshold = 1024 * 100  # 100KB
        self.retry_attempts = 3
        self.retry_delay = 0.1

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            for attempt in range(self.retry_attempts):
                try:
                    value = await self.redis_client.get(key)
                    if not value:
                        return None
                    return self._decompress_if_needed(value)
                except redis.ConnectionError:
                    if attempt == self.retry_attempts - 1:
                        raise
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Store value in cache"""
        try:
            # Compress large values
            if sys.getsizeof(str(value)) > self.compression_threshold:
                value = self._compress_value(value)
                key = f"compressed:{key}"
