import asyncio
import logging
from collections import deque as Deque
from contextlib import asynccontextmanager
from time import monotonic
from typing import Any, Callable, Coroutine, TypeAlias

from pysqlx_engine import PySQLXEngine
from pysqlx_engine._core.logger import logger

ALock = asyncio.Lock
asleep = asyncio.sleep
AQueue = asyncio.Queue
AWorker: TypeAlias = "asyncio.Task[None]"

logging.basicConfig(level=logging.DEBUG)


def aspawn(
    f: Callable[..., Coroutine[Any, Any, None]],
    args: tuple[Any, ...] = (),
    name: str | None = None,
) -> asyncio.Task[None]:
    """
    Equivalent to asyncio.create_task.
    """
    return asyncio.create_task(f(*args), name=name)


class ConnInfo:
    def __init__(self, conn: PySQLXEngine, timeout: float):
        self._conn = conn
        self.timeout = monotonic() + timeout
        self.start = monotonic()
        self.end = 0

    @property
    def can_be_removed(self) -> bool:
        remove = not self._conn.is_healthy() or self.timeout < monotonic()
        logger.debug(f"Checking if connection can be removed: {remove}")
        return remove

    def __str__(self) -> str:
        return f"ConnInfo(conn={self._conn}, timeout={self.timeout}, start={self.start}, end={self.end})"

    async def close(self) -> None:
        logger.debug("Closing connection")
        await self._conn.close()
        self.end = monotonic()
        logger.debug(f"Remove the conn: {self} from pool, the conn was open for {self.end - self.start} seconds")


class Monitor:
    def __init__(self, min_size: int, max_size: int) -> None:
        self.min_size = min_size
        self.max_size = max_size

    async def run(self, pool: AQueue[ConnInfo], lock: asyncio.Lock) -> None:
        while True:
            await asleep(1)
            logger.debug("Monitoring pool")
            async with lock:
                logger.debug(f"Checking pool size: {pool.qsize()}")
                for _ in range(pool.qsize()):
                    conn_info = pool.get_nowait()
                    if conn_info.can_be_removed:
                        if pool.qsize() > self.min_size or not conn_info._conn.is_healthy():
                            logger.debug("Connection can be removed")
                            aspawn(conn_info.close())
                            continue

                    logger.debug("Recycling connection")
                    conn_info.timeout = monotonic() + conn_info.timeout
                    pool.put_nowait(conn_info)


class APool:
    def __init__(self, uri: str, min_size: int, max_size: int, connection_timeout: float = 60.0):
        self.uri = uri
        self.min_size = min_size
        self.max_size = max_size
        self._pool: AQueue[ConnInfo] = asyncio.Queue()
        self._pool_len = 0
        self._conn_timeout = connection_timeout
        self._lock: ALock = asyncio.Lock()
        self._opened = False
        self.monitor = Monitor(min_size=min_size, max_size=max_size)

        PySQLXEngine(uri)  # Check if the URI is valid
        aspawn(self._monitor())

    async def _monitor(self) -> None:
        logger.debug("Starting monitor")
        await self.monitor.run(self._pool, self._lock)

    def __del__(self):
        if getattr(self, "_pool", None):
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.stop())
            except Exception as e:
                logger.error(f"Error while stopping pool: {e}")
                del self._pool

    async def start(self) -> None:
        async with self._lock:
            logger.debug("Starting pool")
            for _ in range(self.min_size):
                conn = PySQLXEngine(self.uri)
                await conn.connect()
                assert conn.is_healthy()
                self._pool.put_nowait(ConnInfo(conn, self._conn_timeout))
                self._pool_len += 1
            self._opened = True

    async def stop(self) -> None:
        async with self._lock:
            logger.debug("Stopping pool")
            for _ in range(self._pool.qsize()):
                conn = await self._pool.get()
                await conn._conn.close()
                self._pool_len -= 1
            self._opened = False

    def _check_open_getconn(self) -> None:
        if not self._opened:
            raise RuntimeError("Pool is closed")

    async def getconn(self) -> ConnInfo:
        self._check_open_getconn()
        async with self._lock:
            if self._pool_len < self.min_size or self._pool.qsize() == 0:
                conn = PySQLXEngine(self.uri)
                await conn.connect()
                assert conn.is_healthy()
                self._pool_len += 1
                return ConnInfo(conn, self._conn_timeout)
            else:
                conn_info = await self._pool.get()
                return conn_info

    async def _getconn_with_timeout(self) -> ConnInfo:
        deadline = monotonic() + self._conn_timeout
        while deadline > monotonic():
            ...

    @asynccontextmanager
    async def get_connection(self): ...


async def main() -> None:
    pool = APool(uri="sqlite:./dev.db", min_size=2, max_size=5, connection_timeout=10)
    await pool.start()

    async with pool.get_connection() as conn:
        q = conn.query_first("SELECT 1")
        await asleep(11)
        async with pool.get_connection() as conn2:
            q2 = conn2.query_first("SELECT 1")
            resp = await asyncio.gather(q, q2)
        logger.info(resp)
        await asleep(5)

    await pool.stop()


asyncio.run(main())
