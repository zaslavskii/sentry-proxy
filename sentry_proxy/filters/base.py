import dataclasses as dc
import typing as t

from proxy.http.parser import HttpParser


@dc.dataclass(frozen=True)
class SentryFilterContext:
    request: HttpParser
    sentry_data: t.Mapping[str, t.Any] = dc.field(default_factory=dict)


class Filter(t.Protocol):
    def __call__(self, context: SentryFilterContext) -> SentryFilterContext:
        ...
