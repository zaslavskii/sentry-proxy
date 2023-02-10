import typing as t
from typing import assert_never

import redis

from sentry_proxy.const import StorageEnum, StrategyEnum, ensure
from sentry_proxy.filters.rate_limiter_filter import IncrementFunc
from sentry_proxy.storage.memory import memory_increment
from sentry_proxy.storage.redis import redis_increment


def increment(
    storage: StorageEnum,
    strategy: StrategyEnum = StrategyEnum.STRICT_PERIOD,
    redis_url: t.Optional[str] = None,
    redis_flush_db_on_start: bool = False,
) -> IncrementFunc:
    match storage:
        case StorageEnum.MEMORY:
            return memory_increment(strategy, {})
        case StorageEnum.REDIS:
            return redis_increment(
                redis.from_url(ensure(redis_url)), strategy, redis_flush_db_on_start
            )
        case _:
            assert_never(storage)
