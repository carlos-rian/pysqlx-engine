import asyncio
from asyncio import Queue, Semaphore
from contextlib import asynccontextmanager
from time import monotonic

from pysqlx_engine import PySQLXEngine

from .abc.base_pool import BaseConnInfo, BaseMonitor, BasePool, Worker, logger
from .errors import PoolAlreadyClosedError, PoolAlreadyStartedError, PoolTimeoutError
from .util import agather, asleep, aspawn

__all__ = ["PySQLXEnginePool"]


class ConnInfo(BaseConnInfo):
	conn: PySQLXEngine

	async def close(self) -> None:
		await super()._aclose()


class Monitor(BaseMonitor):
	pool: "PySQLXEnginePool"

	async def run(self) -> None:
		logger.info("Monitor: Started monitoring the pool.")
		while self.pool._opened:
			self._checking = True
			async with self.pool._monitor_lock:
				await self.pool._monitor_semaphore.acquire()
				try:
					conns_to_check = min(self.pool._pool.qsize(), self.pool._batch_size)
					for _ in range(conns_to_check):
						try:
							conn = self.pool._pool.get_nowait()
						except asyncio.QueueEmpty:
							break

						if self.pool._size > self.pool._max_size:
							logger.debug("Monitor: Pool size is above minimum, closing connection.")
							await self.pool._del_conn_unchecked(conn=conn)

						elif conn.healthy is False or conn.reusable is False:
							logger.debug(f"Connection: {conn} is unhealthy, closing.")
							await self.pool._del_conn_unchecked(conn=conn)

						elif monotonic() >= conn.expires_at:
							logger.debug(f"Monitor: Connection {conn} has expired, renewing.")
							conn.renew_expires_at()
							self.pool._pool.put_nowait(conn)

						else:
							logger.debug(f"Monitor: Reusing healthy connection {conn}.")
							self.pool._pool.put_nowait(conn)

					if self.pool._size < self.pool._min_size:
						logger.debug("Monitor: Pool size is below minimum, creating new connections.")
						new_conns = await agather(
							*[self.pool._new_conn_unchecked() for _ in range(self.pool._min_size - self.pool._size)]
						)
						for conn in new_conns:
							await self.pool._put_conn_unchecked(conn)
					elif self.pool._growing and self.pool._size < self.pool._max_size:
						logger.debug("Monitor: Pool is growing, creating new connections.")
						conn = await self.pool._new_conn_unchecked()
						await self.pool._put_conn_unchecked(conn)
						self.pool._growing = False

				finally:
					# Ensure that semaphore is released even if an error occurs
					self.pool._monitor_semaphore.release()

			self._checking = False
			logger.debug(f"Monitor: Sleeping for {self.pool._check_interval} seconds.")
			await asleep(self.pool._check_interval)

		logger.info("Monitor: Stopped monitoring the pool.")


class PySQLXEnginePool(BasePool):
	"""
	A connection pool for PySQLXEngine connections.

	:param uri: The connection URI.
	:param min_size: The minimum number of connections to keep in the pool.
	:param max_size: The maximum number of connections to keep in the pool.
	:param conn_timeout: The maximum time in seconds to wait for a connection.
	:param keep_alive: The maximum time in seconds to keep a connection alive.
	:param check_interval: The interval in seconds to check the pool for expired connections.
	:param monitor_batch_size: The number of connections to check per interval.

	"""

	def __init__(
		self,
		uri: str,
		min_size: int,
		max_size: int = 10,
		conn_timeout: float = 30.0,
		keep_alive: float = 60 * 15,
		check_interval: float = 5.0,
		monitor_batch_size: int = 10,  # Number of connections to check per interval
	):
		super().__init__(
			uri=uri,
			min_size=min_size,
			max_size=max_size,
			conn_timeout=conn_timeout,
			keep_alive=keep_alive,
			check_interval=check_interval,
		)
		self._pool: Queue[ConnInfo] = Queue(maxsize=self._max_size)
		self._semaphore: Semaphore = Semaphore(self._max_size)
		self._monitor_lock: asyncio.Lock = asyncio.Lock()
		self._monitor_semaphore: Semaphore = Semaphore(1)
		self._workers: list[Worker] = []
		self._opened: bool = False
		self._opening: bool = False
		self._monitor = None
		self._batch_size = monitor_batch_size
		self._lock = asyncio.Lock()

	async def _new_conn_unchecked(self) -> ConnInfo:
		conn = PySQLXEngine(uri=self.uri)
		await conn.connect()
		conn_info = ConnInfo(conn=conn, keep_alive=self._keep_alive)
		self._size += 1
		logger.debug(f"Pool: New connection created: {conn_info} PoolSize: {self._size}")
		return conn_info

	async def _del_conn_unchecked(self, conn: ConnInfo, use_lock: bool = False) -> None:
		if use_lock:
			async with self._lock:
				await conn.close()
				self._size -= 1
		else:
			await conn.close()
			self._size -= 1
		logger.debug(f"Pool: Connection closed: {conn} PoolSize: {self._size}")

	async def _put_conn_unchecked(self, conn: ConnInfo) -> None:
		if conn.healthy and conn.reusable and self._size <= self._max_size:
			try:
				await asyncio.wait_for(self._pool.put(conn), timeout=1)
				logger.debug(f"Pool: Connection returned to pool: {conn}")
			except (asyncio.QueueFull, asyncio.TimeoutError):
				logger.debug(f"Pool: Pool is full. Closing connection: {conn}")
				await self._del_conn_unchecked(conn)
		else:
			logger.debug(f"Pool: Connection is not reusable or expired: {conn}")
			await self._del_conn_unchecked(conn)

	async def _get_ready_conn(self) -> BaseConnInfo:
		try:
			conn = await asyncio.wait_for(self._pool.get(), timeout=BaseConnInfo._jitter(value=0.3))
			return conn
		except asyncio.TimeoutError:
			return

	async def _check_grow(self, value: int) -> None:
		async with self._lock:
			self._waiting += value
			if self._size >= self._max_size:
				return

			self._growing = self._waiting > 1
			logger.debug(f"Pool: Growing: {self._growing} Waiting: {self._waiting}")

	async def _get_conn(self) -> ConnInfo:
		self._check_closed()
		start_time = monotonic()
		deadline = monotonic() + self._conn_timeout
		logger.debug("Getting a ready connection.")
		try:
			start = monotonic()
			await asyncio.wait_for(self._semaphore.acquire(), timeout=self._conn_timeout)
			deadline -= monotonic() - start  # Adjust deadline for time spent waiting for semaphore
			logger.debug(f"Acquired semaphore in {monotonic() - start:.5f} seconds")
		except asyncio.TimeoutError:
			raise PoolTimeoutError("Timeout waiting for a connection semaphore")
		try:
			await self._check_grow(1)
			while True:
				timeout = deadline - monotonic()
				if timeout < 0.0:
					raise PoolTimeoutError("Timeout waiting for a connection")

				conn = await self._get_ready_conn()
				if conn:
					logger.debug(f"Pool: Connection: {conn} retrieved in {monotonic() - start_time:.5f} seconds.")
					return conn

				await asleep(BaseConnInfo._jitter(value=0.3))
		finally:
			await self._check_grow(-1)
			self._semaphore.release()

	async def _put_conn(self, conn: ConnInfo) -> None:
		try:
			async with self._lock:
				await self._put_conn_unchecked(conn)
		finally:
			self._semaphore.release()

	async def _start(self) -> None:
		if self._size > 0 and self._opened:
			logger.error("Pool: Attempted to start an already opened pool.")
			raise PoolAlreadyStartedError("Pool is already started")

		self._opening = True
		logger.info("Pool: Starting the connection pool.")
		async with self._lock:
			tasks = [self._new_conn_unchecked() for _ in range(self._min_size)]
			try:
				conns = await agather(*tasks)
				for conn in conns:
					await self._pool.put(conn)
			except Exception as e:
				logger.error(f"Pool: Error during pool initialization: {e}")
				raise
			self._opened = True
			logger.info(f"Pool: Initialized with {self._min_size} connections.")
		self._opening = False

	async def _start_workers(self) -> None:
		await self._start()
		# Initialize and start the monitor
		self._monitor = aspawn(Monitor(pool=self).run, name="ConnectionMonitor")
		self._workers.append(Worker(self._monitor))
		logger.info("Pool: Workers started.")

	async def start(self) -> None:
		"""Start the pool and create the initial connections."""
		await self._start_workers()

	@asynccontextmanager
	async def connection(self):
		"""
		A context manager that provides a connection from the pool.

		Use this context manager to get a connection from the pool.

		"""
		conn = await self._get_conn()
		try:
			yield conn.conn
		except Exception as e:
			logger.error(f"Pool: Error during connection usage: {e}")
			raise
		finally:
			if conn.conn._on_transaction:
				logger.warning("Transaction is still active, please commit or rollback before closing the connection.")
				await self._del_conn_unchecked(conn, use_lock=True)
			else:
				await self._put_conn(conn)

	async def _stop(self) -> None:
		if not self._opened:
			raise PoolAlreadyClosedError("Pool is already closed")

		logger.info("Pool: Stopping the connection pool.")
		self._opened = False

		# Close all connections
		while not self._pool.empty():
			conn = await self._pool.get()
			await self._del_conn_unchecked(conn)

		# Stop all workers
		for worker in self._workers:
			await worker.afinish()
		self._workers.clear()
		logger.info("Pool: All workers stopped and connections closed.")

	async def stop(self) -> None:
		"""Stop the pool and close all connections."""
		async with self._lock:
			await self._stop()
