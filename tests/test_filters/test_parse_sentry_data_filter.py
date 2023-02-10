import gzip

import pytest

from sentry_proxy.filters.base import SentryFilterContext
from sentry_proxy.filters.parse_sentry_data_filter import ParseSentryDataFilter
from tests.conftest import ZERO_DIVISION_ERROR_PARSED


class TestParseSentryDataFilter:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.filter = ParseSentryDataFilter()

    def test_parse_when_json(self, sentry_filter_context: SentryFilterContext):
        # when
        context = self.filter(sentry_filter_context)

        # then
        assert context.sentry_data == ZERO_DIVISION_ERROR_PARSED

    def test_parse_when_gzipped_json(self, sentry_filter_context: SentryFilterContext):
        # given
        sentry_filter_context.request.body = gzip.compress(
            sentry_filter_context.request.body
        )
        sentry_filter_context.request.add_header(b"content-encoding", b"gzip")

        # when
        context = self.filter(sentry_filter_context)

        # then
        assert context.sentry_data == ZERO_DIVISION_ERROR_PARSED

    def test_skip_when_no_sentry_header(
        self, sentry_filter_context: SentryFilterContext
    ):
        # given
        sentry_filter_context.request.del_header(b"x-sentry-auth")

        # when
        context = self.filter(sentry_filter_context)

        # then
        assert context.sentry_data == {}

    def test_skip_when_not_json(self, sentry_filter_context: SentryFilterContext):
        # given
        sentry_filter_context.request.del_header(b"content-type")

        # when
        context = self.filter(sentry_filter_context)

        # then
        assert context.sentry_data == {}
