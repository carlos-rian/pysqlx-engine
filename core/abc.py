from abc import ABC, abstractmethod


class AbstractEngine(ABC):
    @abstractmethod
    def close(self) -> None:
        """Synchronous method for closing the engine, useful if the underlying engine uses a subprocess"""
        ...

    @abstractmethod
    async def aclose(self) -> None:
        """Asynchronous method for closing the engine, only used if an
        asynchronous client is generated.
        """
        ...

    @abstractmethod
    async def connect(
        self,
        timeout: int = 10,
    ) -> None:
        ...

    @abstractmethod
    async def check_engine(self) -> bool:
        ...
