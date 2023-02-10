from datetime import datetime, timedelta

import pytest

from sentry_proxy.const import StrategyEnum
from sentry_proxy.storage.memory import memory_increment


class TestMemoryIncrement:
    @pytest.fixture
    def strict_period_increment(self):
        return memory_increment(StrategyEnum.STRICT_PERIOD, {})

    @pytest.fixture
    def cooldown_increment(self):
        return memory_increment(StrategyEnum.COOLDOWN, {})

    def test_counter_is_reset_after_strict_period(
        self, strict_period_increment, freezer
    ):
        # given
        now = datetime.utcnow()
        freezer.move_to(now)
        strict_period_increment("key", 1000)
        strict_period_increment("key", 1000)
        strict_period_increment("key", 1000)

        # when not exceeded the ttl
        freezer.move_to(now + timedelta(seconds=1000))
        assert strict_period_increment("key", 1000) == 4

        # when exceeded the ttl
        freezer.move_to(now + timedelta(seconds=1001))
        assert strict_period_increment("key", 1000) == 1

    def test_counter_is_reset_after_cooldown(self, cooldown_increment, freezer):
        # given
        now = datetime.utcnow()
        freezer.move_to(now)
        cooldown_increment("key", 1000)
        cooldown_increment("key", 1000)
        cooldown_increment("key", 1000)

        # when not error happens within the ttl and expiration is moved further
        freezer.move_to(now + timedelta(seconds=1000))
        assert cooldown_increment("key", 1000) == 4

        # when not error happens within the ttl and expiration is moved further
        freezer.move_to(now + timedelta(seconds=2000))
        assert cooldown_increment("key", 1000) == 5

        # when no errors during period and exceeded the ttl
        freezer.move_to(now + timedelta(seconds=3001))
        assert cooldown_increment("key", 1000) == 1
