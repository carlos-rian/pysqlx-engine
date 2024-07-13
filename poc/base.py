import asyncio
import logging
import threading
from abc import abstractmethod
from collections import deque as Deque
from random import random
from time import monotonic
from weakref import ref

from pysqlx_engine import PySQLXEngine, 

logger = logging.getLogger("pysqlx_engine")


class ConnInfo:
    _num_conn: int = 0

    def __init__(self, conn: PySQLXEngine, timeout: float):
        self._num_conn = ConnInfo._num_conn = ConnInfo._num_conn + 1
        self.name = f"conn-{self._num_conn}"
        self.conn = conn

        self.expire_at = monotonic() + self._jitter(value=timeout, min_pc=-0.05, max_pc=0.0)
        self.start_at = monotonic()

    def __repr__(self) -> str:
        return f"<{self.__class__.__module__}.{self.__class__.__name__} {self.name!r} at 0x{id(self):x}>"

    def expires(self) -> bool:
        return self.expire_at < monotonic()

    def healthy(self) -> bool:
        return self.conn.is_healthy()

    async def close(self) -> None:
        await self.conn.close()
        self.expire_at = monotonic()
        print(f"Removed: {self} from pool, the conn was open for {self.expire_at - self.start_at} seconds")

    @classmethod
    def _jitter(cls, value: float, min_pc: float, max_pc: float) -> float:
        """
        Add a random value to *value* between *min_pc* and *max_pc* percent.
        """
        return value * (1.0 + ((max_pc - min_pc) * random()) + min_pc)


class BasePool:
    _num_pool = 0

    def __init__(
        self, uri: str, min_size: int, max_size: int = None, timeout: float = 30.0, max_lifetime: float = 60 * 60
    ):
        self.uri = uri
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self.max_lifetime = max_lifetime

        self._num_pool = BasePool._num_pool = BasePool._num_pool + 1
        self.name = f"{self.__class__.__name__}-{self._num_pool}"

        self._size = 0
        self._pool = Deque()
        self._closed = False

        self._check_size(min_size, max_size)

    def __repr__(self) -> str:
        return f"<{self.__class__.__module__}.{self.__class__.__name__} {self.name!r} at 0x{id(self):x}>"

    @property
    def closed(self) -> bool:
        return self._closed

    def _check_size(self, min_size: int, max_size: int) -> None:
        if max_size is None:
            max_size = min_size

        if min_size <= 0:
            raise ValueError("min_size must be greater than 0")

        elif max_size < min_size:
            raise ValueError("min_size must be less than max_size")

    def _check_closed(self) -> None:
        if self.closed:
            raise ValueError("Pool is closed")


class BaseMonitor:
    def __init__(self, pool: BasePool):
        self.pool = ref(pool)

    def __repr__(self) -> str:
        pool = self.pool()
        name = repr(pool.name) if pool else "<pool is gone>"
        return f"<{self.__class__.__name__} {name} at 0x{id(self):x}>"

    @abstractmethod
    def current_t_name(self) -> str:
        """Return the current thread or task name."""
        ...

    @abstractmethod
    def _run(self) -> None:
        pass

    def run(self) -> None:
        """Run the task.

        This usually happens in a worker. Call the concrete _run()
        implementation, if the pool is still alive.
        """
        pool = self.pool()
        if not pool or pool.closed:
            # Pool is no more working. Quietly discard the operation.
            logger.debug("task run discarded: %s", self)
            return

        logger.debug("task running in %s: %s", self.current_t_name, self)
        self._run(pool)
