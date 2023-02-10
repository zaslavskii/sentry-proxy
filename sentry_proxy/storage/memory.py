import typing as t
from threading import Lock
from time import time

from sentry_proxy.const import StrategyEnum


def memory_increment(
    strategy: StrategyEnum, storage: t.MutableMapping[str, t.Tuple[int, int]]
) -> t.Callable[[str, int], int]:
    lock = Lock()

    def __increment(key: str, ttl: int) -> int:
        with lock:
            curr = int(time())
            ts, counter = storage.setdefault(key, (curr, 0))

            if (curr - ts) > ttl:
                storage[key] = (curr, 1)
            else:
                storage[key] = (ts, counter + 1)

            if strategy == StrategyEnum.COOLDOWN:
                storage[key] = (curr, storage[key][1])

            return storage[key][1]

    return __increment
