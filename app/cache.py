from diskcache import Cache
import os

CACHE_DIR = os.getenv("CACHE_DIR", ".cache")
cache = Cache(CACHE_DIR)

def get_cache(key: str):
    return cache.get(key)

def set_cache(key: str, value, ttl: int):
    cache.set(key, value, expire=ttl)