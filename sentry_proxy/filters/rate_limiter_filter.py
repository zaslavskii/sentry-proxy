import logging
import typing as t

from proxy.http.exception import HttpRequestRejected

from sentry_proxy.const import TemplateKeysEnum
from sentry_proxy.filters.base import Filter, SentryFilterContext

logger = logging.getLogger(__name__)

IncrementFunc = t.Callable[[str, int], int]


class RateLimiterFilter(Filter):
    def __init__(
        self, increment: IncrementFunc, template: str, ttl: int, rate: int
    ) -> None:
        self._increment = increment
        self._template = template
        self._ttl = ttl
        self._rate = rate

    def __call__(self, context: SentryFilterContext) -> SentryFilterContext:
        logger.debug("Running filter: %s", self.__class__.__name__)

        if not context.sentry_data:
            logger.debug("No parsed sentry data -> skipping")
            return context

        ctx = self.__context(context.sentry_data)
        logger.debug("Context: %s", ctx)

        key = self.__key(ctx)
        counter = self._increment(key, self._ttl)
        logger.debug("%s [%s/%s, ttl=%s]", key, counter, self._rate, self._ttl)

        if counter >= self._rate:
            raise HttpRequestRejected(
                status_code=429,
                reason=b"Too many errors of this type",
            )

        return context

    def __key(self, ctx: t.Mapping[str, t.Optional[str]]) -> str:
        return self._template.format(**ctx)

    def __context(self, data: t.Mapping[str, t.Any]) -> t.Mapping[str, t.Optional[str]]:
        # assume there is always at least 1 exception
        try:
            exception = data["exception"]["values"][0]

        except (KeyError, IndexError, TypeError):
            logger.exception("Exception not found in data")
            exception = {}

        return {
            TemplateKeysEnum.ENVIRONMENT: data.get("environment"),
            TemplateKeysEnum.MODULE: exception.get("module"),
            TemplateKeysEnum.LEVEL: data.get("level"),
            TemplateKeysEnum.EXCEPTION: exception.get("type"),
            TemplateKeysEnum.MESSAGE: exception.get("value"),
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(ttl={self._ttl}, rate={self._rate}, template={self._template})"
