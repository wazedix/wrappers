# -*- coding: utf-8 -*-

from cache.memory import MemoryCache
from cache.redis_wrap import RedisCache
import logging
import time

logger = logging.getLogger(__name__)


def test_cache_memory():
    cache = MemoryCache.instance()
    cache.set("key", "value", 1)
    assert cache.get("key") == "value"
    time.sleep(1)
    assert cache.get("key") is None


def test_cache_redis():
    redis_conf = [{
        "host": "localhost",
        "port": 6379+i,
    } for i in range(3)]
    cache = RedisCache.instance("test", redis_conf)
    cache.set("key", "value", 1)
    assert cache.get("key") == "value"
    time.sleep(1)
    assert cache.get("key") is None


if __name__ == "__main__":
    test_cache_memory()
    test_cache_redis()
