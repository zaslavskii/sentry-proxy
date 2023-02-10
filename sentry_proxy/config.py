import logging
from os import environ

from sentry_proxy.const import StorageEnum, StrategyEnum, TemplateKeysEnum

# fmt: off
LOG_LEVEL = str(environ.get("SENTRY_PROXY_LOG_LEVEL", "INFO"))
KEY_FORMAT = str(environ.get("SENTRY_PROXY_KEY_FORMAT", f"{{{TemplateKeysEnum.ENVIRONMENT}}}::{{{TemplateKeysEnum.EXCEPTION}}}"))
TTL = int(environ.get("SENTRY_PROXY_TTL", 30))
RATE = int(environ.get("SENTRY_PROXY_RATE", 10))
STRATEGY = StrategyEnum(str(environ.get("SENTRY_PROXY_STRATEGY", StrategyEnum.STRICT_PERIOD)).lower())
STORAGE = StorageEnum(str(environ.get("SENTRY_PROXY_STORAGE", StorageEnum.MEMORY)).lower())
REDIS_URL = str(environ.get("SENTRY_PROXY_REDIS_URL", "redis://localhost:6379/0"))
REDIS_FLUSHDB_ON_START = (str(environ.get("SENTRY_PROXY_REDIS_FLUSHDB_ON_START", "no")).lower() == "yes")
# fmt: on

try:
    KEY_FORMAT.format(**{str(k): "" for k in TemplateKeysEnum})

except KeyError as key:
    raise ValueError(f'SENTRY_PROXY_KEY_FORMAT has unknown template var "{key}"')

logging.getLogger("sentry_proxy").setLevel(LOG_LEVEL)
