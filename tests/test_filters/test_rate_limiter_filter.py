import pytest
from proxy.http.exception import HttpRequestRejected

from sentry_proxy.const import StrategyEnum, TemplateKeysEnum
from sentry_proxy.filters.base import SentryFilterContext
from sentry_proxy.filters.rate_limiter_filter import RateLimiterFilter
from sentry_proxy.storage.memory import memory_increment
from tests.conftest import ZERO_DIVISION_ERROR_DEFAULT_TEMPLATE, ZERO_DIVISION_ERROR_KEY


class TestRateLimiterFilter:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.storage = {}
        self.filter = RateLimiterFilter(
            increment=memory_increment(StrategyEnum.STRICT_PERIOD, self.storage),
            template=ZERO_DIVISION_ERROR_DEFAULT_TEMPLATE,
            ttl=10000,
            rate=2,
        )

    def test_skip_when_no_parsed_data(self, sentry_filter_context: SentryFilterContext):
        # then
        assert sentry_filter_context == self.filter(sentry_filter_context)

    def test_pass_when_limit_is_not_exceeded(
        self, sentry_filter_context_parsed: SentryFilterContext
    ):
        # when
        self.filter(sentry_filter_context_parsed)

        # then
        assert self.storage.keys() == {ZERO_DIVISION_ERROR_KEY}
        assert self.storage[ZERO_DIVISION_ERROR_KEY][1] == 1

    def test_all_template_variables_are_formatted(
        self, sentry_filter_context_parsed: SentryFilterContext
    ):
        # given
        template = ":".join(f"{{{k}}}" for k in TemplateKeysEnum)
        expected = "dev.chainstack.com:None:error:ZeroDivisionError:division by zero"
        instance = RateLimiterFilter(
            increment=memory_increment(StrategyEnum.STRICT_PERIOD, self.storage),
            template=template,
            ttl=1,
            rate=2,
        )

        # when
        instance(sentry_filter_context_parsed)

        # then
        assert self.storage.keys() == {expected}
        assert self.storage[expected][1] == 1

    def test_pass_when_key_is_expired(
        self, sentry_filter_context_parsed: SentryFilterContext, freezer
    ):
        # when
        self.filter(sentry_filter_context_parsed)
        freezer.move_to("2030-05-20")

        # then
        self.filter(sentry_filter_context_parsed)
        assert self.storage.keys() == {ZERO_DIVISION_ERROR_KEY}
        assert self.storage[ZERO_DIVISION_ERROR_KEY][1] == 1

    def test_throw_when_limit_is_exceeded(
        self, sentry_filter_context_parsed: SentryFilterContext
    ):
        # when
        self.filter(sentry_filter_context_parsed)

        # then
        with pytest.raises(HttpRequestRejected):
            self.filter(sentry_filter_context_parsed)

        assert self.storage.keys() == {ZERO_DIVISION_ERROR_KEY}
        assert self.storage[ZERO_DIVISION_ERROR_KEY][1] == 2
