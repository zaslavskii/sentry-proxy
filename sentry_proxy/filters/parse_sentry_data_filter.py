import dataclasses as dc
import gzip
import json
import logging

from sentry_proxy.filters.base import Filter, SentryFilterContext

logger = logging.getLogger(__name__)


class ParseSentryDataFilter(Filter):
    def __call__(self, context: SentryFilterContext) -> SentryFilterContext:
        sentry_data = {}

        if not context.request.has_header(b"x-sentry-auth"):
            logger.debug("No x-sentry-auth -> skipping")

        elif not (
            context.request.has_header(b"content-type")
            and context.request.header(b"content-type") == b"application/json"
        ):
            logger.debug("Not a json -> skipping")

        elif context.request.body is None:
            logger.debug("Body is empty -> skipping")

        elif (
            context.request.has_header(b"content-encoding")
            and context.request.header(b"content-encoding") == b"gzip"
        ):
            logger.debug("Decompressing gzip")
            sentry_data = json.loads(gzip.decompress(context.request.body))

        else:
            sentry_data = json.loads(context.request.body)

        logger.debug("Parsed sentry event: %s", sentry_data)

        return dc.replace(context, sentry_data=sentry_data)
