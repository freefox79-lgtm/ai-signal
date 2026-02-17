import redis
import os
import json
import datetime
from dotenv import load_dotenv
# Load environment variables
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
else:
    load_dotenv()


class CacheManager:
    """
    Handles fast retrieval of synthesized signals using Redis.
    Used to reduce database load and improve UI performance.
    """
    
    def __init__(self):
        # Prefer REDIS_URL (Render/Production)
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            self.r = redis.from_url(redis_url, decode_responses=True)
        else:
            # Fallback to host/password (Local/Docker)
            redis_pwd = os.getenv("REDIS_PASSWORD", "aisignal2026_secure")
            redis_host = os.getenv("REDIS_HOST", "localhost")
            self.r = redis.Redis(
                host=redis_host,
                port=6379,
                password=redis_pwd,
                decode_responses=True
            )

    def set_signal(self, key, data, source="unknown", expiry=3600):
        """Cache a signal with automatic metadata (timestamp, source)."""
        try:
            payload = {
                "data": data,
                "metadata": {
                    "source": source,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "cached": True
                }
            }
            self.r.set(f"signal:{key}", json.dumps(payload), ex=expiry)
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

    def cached(self, source, expiry=3600):
        """Decorator for transparent caching of API responses."""
        def decorator(func):
            def wrapper(self_obj, *args, **kwargs):
                # Simple key based on function name and arguments
                # Skipping 'self_obj' in args for key generation
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                cached_data = self.get_signal(cache_key)
                
                if cached_data:
                    return cached_data["data"]
                
                # Fetch fresh data
                result = func(self_obj, *args, **kwargs)
                if result:
                    self.set_signal(cache_key, result, source=source, expiry=expiry)
                return result
            return wrapper
        return decorator

if __name__ == "__main__":
    cache = CacheManager()
    
    @cache.cached(source="TestSystem", expiry=60)
    def fetch_test_data(query):
        print(f"Fetching fresh data for {query}...")
        return {"result": f"Data for {query}"}

    # First call - Fresh
    print(fetch_test_data("AI"))
    # Second call - Cached
    print(fetch_test_data("AI"))
