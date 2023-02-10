import typing as t

from proxy.http.parser import HttpParser
from proxy.http.proxy import HttpProxyBasePlugin

from sentry_proxy import config
from sentry_proxy.filters.base import Filter, SentryFilterContext
from sentry_proxy.filters.parse_sentry_data_filter import ParseSentryDataFilter
from sentry_proxy.filters.rate_limiter_filter import RateLimiterFilter
from sentry_proxy.storage.factory import increment


class SentryPlugin(HttpProxyBasePlugin):
    filters: t.Sequence[Filter] = (
        ParseSentryDataFilter(),
        RateLimiterFilter(
            increment=increment(
                storage=config.STORAGE,
                strategy=config.STRATEGY,
                redis_url=config.REDIS_URL,
                redis_flush_db_on_start=config.REDIS_FLUSHDB_ON_START,
            ),
            template=config.KEY_FORMAT,
            ttl=config.TTL,
            rate=config.RATE,
        ),
    )

    def handle_client_request(
        self,
        request: HttpParser,
    ) -> t.Optional[HttpParser]:
        context = SentryFilterContext(request=request)

        for f in self.filters:
            context = f(context)

        return context.request
