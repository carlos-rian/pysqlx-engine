from abc import ABC, abstractmethod

from typing_extensions import TypeVar

from .const import PROVIDER

T = TypeVar("T")


class AbstractDatabaseType(ABC):
    """
    Abstract database type

    You can create a custom type by inheriting this class.

    Implement the `convert` method to convert the value to the database type.

    """

    @abstractmethod
    def __init__(self, value: T): ...

    @abstractmethod
    def convert(self, provider: PROVIDER, field: str = "") -> T: ...
