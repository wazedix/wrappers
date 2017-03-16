# -*- coding: utf-8 -*-

import time
import logging

logger = logging.getLogger("root")


class MemoryCache(object):

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.__cache = {}

    def clear(self):
        self.__cache = {}

    def set(self, key, value, seconds=0):
        self.__cache[key] = (value, time.time() + seconds if seconds else 0)

    def get(self, key):
        value = self.__cache.get(key)
        if not value:
            return None
        if value[1] and time.time() > value[1]:
            del self.__cache[key]
            return None
        return value[0]

    def delete(self, key):
        try:
            del self.__cache[key]
        except Exception:
            pass
