import redis
import os
import json
from dotenv import load_dotenv

load_dotenv(".env.local")

class CacheManager:
    """
    Handles fast retrieval of synthesized signals using Redis.
    Used to reduce database load and improve UI performance.
    """
    
    def __init__(self):
        # Prefer REDIS_PASSWORD from .env.local
        redis_pwd = os.getenv("REDIS_PASSWORD", "aisignal2026_secure")
        self.r = redis.Redis(
            host='localhost',
            port=6379,
            password=redis_pwd,
            decode_responses=True
        )

    def set_signal(self, key, data, expiry=3600):
        """Cache a signal for a specified duration (default 1h)."""
        try:
            self.r.set(f"signal:{key}", json.dumps(data), ex=expiry)
            return True
        except Exception as e:
            print(f"[CACHE] Set Error: {e}")
            return False

    def get_signal(self, key):
        """Retrieve a cached signal."""
        try:
            data = self.r.get(f"signal:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            print(f"[CACHE] Get Error: {e}")
            return None

if __name__ == "__main__":
    cache = CacheManager()
    # Test
    test_data = {"id": "S123", "value": "Strong Buy AI Semi"}
    if cache.set_signal("test_1", test_data):
        print(f"[CACHE] Success: {cache.get_signal('test_1')}")
