import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx


class AbstractEngine(ABC):
    url: str
    process: subprocess.Popen
    session: httpx.AsyncClient

    @abstractmethod
    async def connect(self, timeout: int = 10) -> None:
        ...

    @abstractmethod
    async def connected(self) -> bool:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def spawn(self, file: Path, timeout: int = 10) -> None:
        ...

    async def _check_connect(self) -> None:
        ...
