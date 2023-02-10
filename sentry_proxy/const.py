import typing as t
from enum import StrEnum, auto

T = t.TypeVar("T")


class StrategyEnum(StrEnum):
    STRICT_PERIOD = auto()
    COOLDOWN = auto()


class StorageEnum(StrEnum):
    REDIS = auto()
    MEMORY = auto()


class TemplateKeysEnum(StrEnum):
    ENVIRONMENT = auto()
    MODULE = auto()
    LEVEL = auto()
    EXCEPTION = auto()
    MESSAGE = auto()


class ValueRequired(ValueError):
    def __init__(self) -> None:
        super().__init__("Expected not None value")


def ensure(v: t.Optional[T]) -> T:
    if v is None:
        raise ValueRequired()
    return v
