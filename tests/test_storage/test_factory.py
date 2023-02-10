from uuid import uuid4

import pytest

from sentry_proxy.const import StorageEnum, ValueRequired
from sentry_proxy.storage.factory import increment


class TestIncrementFactory:
    def test_memory_increment_is_provided(self):
        # given
        instance = increment(storage=StorageEnum.MEMORY)

        # then
        assert instance(str(uuid4()), 10) == 1

    def test_redis_increment_is_provided(self):
        # then
        with pytest.raises(ValueRequired):
            increment(storage=StorageEnum.REDIS)
