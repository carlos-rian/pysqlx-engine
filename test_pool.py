import asyncio
import logging
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

    @property
    def can_be_removed(self) -> bool:
        remove = not self._conn.is_healthy() or self.timeout < monotonic()
        logger.debug(f"Checking if connection can be removed: {remove}")
        return remove


class Monitor:
    async def run(self, pool: AQueue[ConnInfo], lock: asyncio.Lock) -> None:
        while True:
            await asleep(1)
            logger.debug("Monitoring pool")
            async with lock:
                logger.debug(f"Checking pool size: {pool.qsize()}")
                for _ in range(pool.qsize()):
                    conn_info = pool.get_nowait()
                    if conn_info.can_be_removed:
                        await conn_info._conn.close()
                    else:
                        pool.put_nowait(conn_info)


class APool:
    def __init__(self, uri: str, min_size: int, max_size: int, timeout: float = 60.0):
        self.uri = uri
        self.min_size = min_size
        self.max_size = max_size
        self._pool: AQueue[ConnInfo] = asyncio.Queue()
        self._pool_len = 0
        self._timeout = timeout
        self._lock: ALock = asyncio.Lock()
        self.monitor = Monitor()

        PySQLXEngine(uri)  # Check if the URI is valid
        asyncio.create_task(self._monitor())

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
                self._pool.put_nowait(ConnInfo(conn, self._timeout))
                self._pool_len += 1

    async def stop(self) -> None:
        async with self._lock:
            logger.debug("Stopping pool")
            for _ in range(self._pool.qsize()):
                conn = await self._pool.get()
                await conn._conn.close()
                self._pool_len -= 1

    async def getconn(self) -> ConnInfo:
        logger.debug(f"Pool size: {self._pool_len}")
        if self._pool.qsize() > 0:
            logger.debug("Getting connection from pool")
            conn_info = self._pool.get_nowait()
            if conn_info.can_be_removed:
                await conn_info._conn.close()
                self._pool_len -= 1
            else:
                return conn_info

        logger.debug("Creating new connection")
        conn = PySQLXEngine(self.uri)
        await conn.connect()
        self._pool_len += 1
        return ConnInfo(conn, self._timeout)

    @asynccontextmanager
    async def get_connection(self):
        async with self._lock:
            conn = await self.getconn()
            try:
                logger.debug("Yielding connection to caller")
                yield conn._conn
            finally:
                logger.debug("Checking if connection can be returned to pool")
                if conn.can_be_removed:
                    logger.debug("Connection can't be returned to pool")
                    await conn._conn.close()
                    self._pool_len -= 1
                else:
                    logger.debug("Connection can be returned to pool")
                    self._pool.put_nowait(conn)


async def main() -> None:
    pool = APool("sqlite:./dev.db", 2, 5)
    await pool.start()

    async with pool.get_connection() as conn:
        q = await conn.query_first("SELECT 1")
        logger.info(q)
        await asleep(5)

    await pool.stop()


asyncio.run(main())
