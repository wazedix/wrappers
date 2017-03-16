# -*- coding: utf-8 -*-

import redis
import time
import functools
import logging

logger = logging.getLogger(__name__)


class RedisIndexException(Exception):
    pass


class RedisCache(object):

    DEFAULT_RESULT = "--default_result--"

    @classmethod
    def instance(cls, backend, redis_conf, reconnect_interval=60):
        _instance = "_%s_instance" % backend
        if not hasattr(cls, _instance):
            ins = cls(redis_conf, reconnect_interval)
            setattr(cls, _instance, ins)
        return getattr(cls, _instance)

    def __init__(self, redis_conf, reconnect_interval):
        self.index = None
        self.reconnect_interval = reconnect_interval
        self.redis_conf = redis_conf
        self.redis_host = [conf["host"] for conf in self.redis_conf]
        self.redis = self._connect()

    def _connect(self):
        self._reconnect = 0
        redis_list = []
        for cache_conf in self.redis_conf:
            cache_conf["socket_timeout"] = cache_conf.get("socket_timeout", 5)
            try:
                r = redis.StrictRedis(**cache_conf)
                r.set("--test_key--", "--test_data--", 10)
                r.get("--test_key--")
            except Exception, e:
                logger.error("redis connect error: %s", e)
                self._reconnect = time.time() + self.reconnect_interval
                redis_list.append(None)
            else:
                redis_list.append(r)
        if not len([r_ for r_ in redis_list if r_ is not None]):
            raise Exception("redis all fail: %s %s" % (
                ",".join(self.redis_host), e))
        return redis_list

    def _call_redis_method(self, method, *args, **kwargs):
        result = self.DEFAULT_RESULT
        # last_result = self.DEFAULT_RESULT
        for index, r in enumerate(self.redis):
            try:
                result = self._call_index_redis_method(
                    method, index, *args, **kwargs)
            except RedisIndexException:
                pass
        if result == self.DEFAULT_RESULT:
            raise Exception("redis all dead: %s" % ",".join(self.redis_host))
        return result

    def _call_index_redis_method(self, method, index, *args, **kwargs):
        """
        Only use a given redis.
        If connect error, do not failover here. Just raise an exception,
        and let the caller retry if necessary.
        """
        _redis = self.redis[index]
        try:
            result = getattr(_redis, method)(*args, **kwargs)
        except Exception, e:
            self._reconnect = self._reconnect or \
                time.time() + self.reconnect_interval
            logger.warning("redis error (%s) %s: %s(*%.30s, **%.30s)",
                           self.redis_host[index], e, method, args, kwargs)
            raise RedisIndexException(
                "redis connect error for index %d" % index)
        return result

    def __getattr__(self, method):
        if self._reconnect and self._reconnect <= time.time():
            logger.info("Try to reconnect redis")
            self.redis = self._connect()
        if self.index is not None:
            # self.index should be None before call _call_index_redis_method
            tmp_index, self.index = self.index, None
            return functools.partial(
                self._call_index_redis_method, method, tmp_index)
        return functools.partial(self._call_redis_method, method)

    def set_index(self, index):
        """
        use a given index
        Example:
            r.set_index(2).zinterstore(foo, bar)
        """
        assert index < len(self.redis_conf)
        self.index = index
        return self
