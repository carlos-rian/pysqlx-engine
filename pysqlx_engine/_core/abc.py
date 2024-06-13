from abc import ABC, abstractmethod

from typing_extensions import TypeVar

from .const import PROVIDER

T = TypeVar("T")


class AbstractDatabaseType(ABC):
    @abstractmethod
    def __init__(self, value: T): ...

    @abstractmethod
    def convert(self, provider: PROVIDER, field: str = "") -> T: ...
