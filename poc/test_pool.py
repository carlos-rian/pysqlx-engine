import asyncio
import threading
from contextlib import asynccontextmanager
from time import monotonic
from weakref import ref

from pysqlx_engine._core.aconn import PySQLXEngine

from .base import BaseConnInfo, BaseMonitor, BasePool, logger
from .errors import PoolAlreadyStarted, PoolTimeout


def current_thread_name() -> str:
	return threading.current_thread().name


def current_task_name() -> str:
	t = asyncio.current_task()
	return t.get_name() if t else "<no task>"


class ConnInfo(BaseConnInfo):
	async def close(self) -> None:
		return await super()._aclose()


class ConnInfoSync(BaseConnInfo):
	def close(self) -> None:
		return super()._close()


class PySQLXEnginePool(BasePool):
	def __init__(
		self,
		uri: str,
		min_size: int,
		max_size: int = None,
		conn_timeout: float = 30.0,
		keep_alive: float = 60 * 15,
		check_interval: float = 5.0,
	):
		super().__init__(
			uri=uri,
			min_size=min_size,
			max_size=max_size,
			conn_timeout=conn_timeout,
			keep_alive=keep_alive,
			check_interval=check_interval,
		)
		self._lock = asyncio.Lock()

	def __del__(self) -> None:
		if getattr(self, "_pool", None):
			asyncio.run(self.stop())

	async def _new_conn(self) -> BaseConnInfo:
		conn = PySQLXEngine(uri=self.uri)
		await conn.connect()
		self._size += 1
		return ConnInfo(conn=conn, keep_alive=self._keep_alive)

	async def _del_conn(self, conn: BaseConnInfo) -> None:
		await conn.close()
		self._size -= 1

	async def _put_conn(self, conn: BaseConnInfo) -> None:
		self._check_closed()
		if not conn.reusable:
			await self._del_conn(conn)
			conn = await self._new_conn()

		self._pool.append(conn)
		self._num_pool += 1

	async def _get_ready_conn(self) -> BaseConnInfo:
		if self._pool:
			conn = self._pool.popleft()
			return conn

		if self._size < self._max_size:
			conn = await self._new_conn()
			return conn

	async def _get_conn(self) -> BaseConnInfo:
		self._check_closed()
		deadline = monotonic() + self._conn_timeout

		while True:
			timeout = deadline - monotonic()

			if timeout < 0.0:
				raise PoolTimeout("Timeout waiting for a connection")

			conn = await self._get_ready_conn()
			if conn:
				return conn

			await asyncio.sleep(0.1)

	async def _start(self) -> None:
		if self._num_pool > 0:
			raise PoolAlreadyStarted("Pool is already started")

		async with self._lock:
			for _ in range(self._min_size):
				conn = await self._new_conn()
				await self._put_conn(conn)
			self._opened = True

	async def _start_workers(self) -> None:
		if self._opened and self._num_pool > 0:
			return

		asyncio.create_task(self._start())
		asyncio.create_task(Monitor(pool=ref(self)).run())

	@asynccontextmanager
	async def get_connection(self):
		conn = await self._get_conn()
		try:
			yield conn.conn
		finally:
			await self._put_conn(conn)

	async def stop(self) -> None:
		async with self._lock:
			self._opened = False
			while self._pool:
				conn = self._pool.popleft()
				await self._del_conn(conn)


class Monitor(BaseMonitor):
	def __init__(self, pool: BasePool):
		super().__init__(pool)
		self._lock = asyncio.Lock()

	def current_t_name(self) -> str:
		return current_task_name()

	async def run(self) -> None:
		while True:
			async with self._lock:
				pool = self.pool()
				if pool._opened:
					for _ in range(len(pool._pool)):
						conn = pool._pool.popleft()
						if conn.healthy is False:
							logger.debug(f"Connection: {conn} is unhealthy, closing.")
							await pool._del_conn(conn=conn)

						elif (pool._min_size > pool._size < pool._max_size) or pool._size > pool._max_size:
							# close the connection
							logger.debug(f"Connection: {conn} health, but pool is full, closing.")
							await pool._del_conn(conn=conn)

						elif conn.expires:
							# reuse the connection
							logger.debug(f"Connection: {conn} health, renewing.")
							conn.renew_expire_at()
							await pool._put_conn(conn=conn)

						else:
							# reuse the connection
							logger.debug(f"Connection: {conn} health, reusing.")
							await pool._put_conn(conn=conn)
				else:
					logger.debug("Pool is closed, waiting for the next check.")

			logger.debug(f"Sleeping for {pool._check_interval} seconds")
			await asyncio.sleep(pool._check_interval)


class MonitorSync(BaseMonitor): ...
