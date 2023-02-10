import json
import typing as t

import pytest
import redis
from proxy.common.utils import build_http_request
from proxy.http import httpMethods
from proxy.http.parser import HttpParser

from sentry_proxy import config
from sentry_proxy.filters.base import SentryFilterContext

ZERO_DIVISION_ERROR_RAW = b'{"level":"error","exception":{"values":[{"module":null,"type":"ZeroDivisionError","value":"division by zero","mechanism":{"type":"excepthook","handled":false},"stacktrace":{"frames":[{"filename":"dummy.py","abs_path":"/Users/zas/Code/chainstack/sentry-proxy/dummy.py","function":"<module>","module":"__main__","lineno":15,"pre_context":["    http_proxy=SENTRY_PROXY,","    environment=\\"dev.chainstack.com\\",","    ca_certs=SENTRY_PROXY_CA_CERT,",")","if __name__ == \'__main__\':"],"context_line":"    division_by_zero = 1 / 0","post_context":[],"vars":{"__name__":"\'__main__\'","__doc__":"None","__package__":"None","__loader__":"<_frozen_importlib_external.SourceFileLoader object at 0x100635310>","__spec__":"None","__annotations__":{},"__builtins__":"<module \'builtins\' (built-in)>","__file__":"\'/Users/zas/Code/chainstack/sentry-proxy/./dummy.py\'","__cached__":"None","init":"<function _init at 0x1015a5e40>"},"in_app":true}]}}]},"event_id":"bab88afb3bdd499c81784830b608a650","timestamp":"2023-02-10T16:37:58.843021Z","breadcrumbs":{"values":[]},"transaction_info":{},"contexts":{"runtime":{"name":"CPython","version":"3.11.1","build":"3.11.1 (main, Dec 23 2022, 09:25:23) [Clang 14.0.0 (clang-1400.0.29.202)]"}},"modules":{"certifi":"2022.12.7","setuptools":"65.6.3","packaging":"23.0","pip":"22.3.1","attrs":"22.2.0","pytest":"7.2.1","redis":"4.4.2","async-timeout":"4.0.2","proxy.py":"2.4.3","iniconfig":"2.0.0","urllib3":"1.26.14","sentry-sdk":"1.14.0","pluggy":"1.0.0","sentry-proxy":"0.1.0"},"extra":{"sys.argv":["./dummy.py"]},"release":"a2b89131e76545aa316826923683cc6f21ca5ea5","environment":"dev.chainstack.com","server_name":"MacBook-Pro-Anton.local","sdk":{"name":"sentry.python","version":"1.14.0","packages":[{"name":"pypi:sentry-sdk","version":"1.14.0"}],"integrations":["argv","atexit","dedupe","excepthook","logging","modules","redis","stdlib","threading"]},"platform":"python","_meta":{"exception":{"values":{"0":{"stacktrace":{"frames":{"0":{"vars":{"":{"len":13}}}}}}}}}}'
ZERO_DIVISION_ERROR_PARSED = json.loads(ZERO_DIVISION_ERROR_RAW)
ZERO_DIVISION_ERROR_KEY = "ZeroDivisionError"
ZERO_DIVISION_ERROR_DEFAULT_TEMPLATE = "{exception}"


def zero_division_error_request(
    url: bytes = b"https://example.com",
    headers: t.Optional[t.Dict[bytes, bytes]] = None,
):
    return build_http_request(
        method=httpMethods.POST,
        url=url,
        content_type=b"application/json",
        body=ZERO_DIVISION_ERROR_RAW,
        headers={b"x-sentry-auth": b"qwertyui", **(headers or {})},
    )


@pytest.fixture
def sentry_filter_context():
    return SentryFilterContext(
        request=HttpParser.request(raw=zero_division_error_request())
    )


@pytest.fixture
def sentry_filter_context_parsed():
    return SentryFilterContext(
        request=HttpParser.request(raw=zero_division_error_request()),
        sentry_data=ZERO_DIVISION_ERROR_PARSED,
    )


@pytest.fixture
def redis_connection():
    return redis.from_url(config.REDIS_URL)
