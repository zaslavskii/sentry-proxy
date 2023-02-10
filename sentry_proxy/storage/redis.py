import typing as t
from typing import assert_never

import redis

from sentry_proxy.const import StrategyEnum


def redis_increment(
    r: redis.Redis, strategy: StrategyEnum, flush_db: bool  # type: ignore
) -> t.Callable[[str, int], int]:
    if flush_db:
        r.flushdb()

    def __strict_period_increment(key: str, ttl: int) -> int:
        pipe = r.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, ttl, True)
        return pipe.execute()[0]

    def __cooldown_increment(key: str, ttl: int) -> int:
        pipe = r.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, ttl)
        return pipe.execute()[0]

    match strategy:
        case StrategyEnum.STRICT_PERIOD:
            return __strict_period_increment
        case StrategyEnum.COOLDOWN:
            return __cooldown_increment
        case strategy:
            assert_never(strategy)
