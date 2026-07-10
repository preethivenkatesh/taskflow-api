"""
Cache Service - Simple in-memory caching
BUG: Memory and concurrency issues!
"""
import time
from typing import Any, Optional

class CacheService:
    def __init__(self):
        self.cache = {}
        self.expiry_times = {}

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set a cache value with TTL"""
        # BUG 1: No limit on cache size, can cause memory issues
        self.cache[key] = value
        self.expiry_times[key] = time.time() + ttl

    def get(self, key: str) -> Optional[Any]:
        """Get a cache value"""
        # BUG 2: Doesn't check if key is expired before returning
        return self.cache.get(key)

    def delete(self, key: str):
        """Delete a cache entry"""
        # BUG 3: Doesn't check if key exists, will raise KeyError
        del self.cache[key]
        del self.expiry_times[key]

    def clear_expired(self):
        """Clear expired cache entries"""
        # BUG 4: Modifying dict while iterating over it
        current_time = time.time()
        for key in self.cache:
            if self.expiry_times[key] < current_time:
                del self.cache[key]
                del self.expiry_times[key]

    def get_stats(self):
        """Get cache statistics"""
        # BUG 5: Division by zero if cache is empty
        hit_rate = len(self.cache) / (len(self.cache) + 100)
        return {
            'size': len(self.cache),
            'hit_rate': hit_rate
        }
