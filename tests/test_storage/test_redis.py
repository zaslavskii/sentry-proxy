from time import sleep
from uuid import uuid4

import pytest

from sentry_proxy.const import StrategyEnum
from sentry_proxy.storage.redis import redis_increment


@pytest.mark.integration
class TestRedisIncrement:
    @pytest.fixture
    def strict_period_increment(self, redis_connection):
        return redis_increment(redis_connection, StrategyEnum.STRICT_PERIOD, False)

    @pytest.fixture
    def cooldown_increment(self, redis_connection):
        return redis_increment(redis_connection, StrategyEnum.COOLDOWN, False)

    def test_counter_is_reset_after_strict_period(self, strict_period_increment):
        # given
        key = str(uuid4())
        strict_period_increment(key, 5)

        # when not exceeded the ttl
        assert strict_period_increment(key, 5) == 2

        sleep(5)

        # when exceeded the ttl
        assert strict_period_increment(key, 5) == 1

    def test_counter_is_reset_after_cooldown(self, cooldown_increment):
        # given
        key = str(uuid4())
        cooldown_increment(key, 5)

        sleep(3)

        # when not error happens within the ttl and expiration is moved further
        assert cooldown_increment(key, 5) == 2

        sleep(3)

        # when not error happens within the ttl and expiration is moved further
        assert cooldown_increment(key, 5) == 3

        sleep(6)

        # when no errors during period and exceeded the ttl
        assert cooldown_increment(key, 5) == 1
