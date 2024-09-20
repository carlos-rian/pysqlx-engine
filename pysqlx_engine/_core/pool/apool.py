import asyncio
from asyncio import Queue, Semaphore
from contextlib import asynccontextmanager
from time import monotonic
from weakref import ReferenceType, ref

from pysqlx_engine import PySQLXEngine

from ..abc.base_pool import BaseConnInfo, BaseMonitor, BasePool, Worker, logger
from ..errors import PoolAlreadyStartedError, PoolTimeoutError
from ..util import agather, asleep, aspawn_loop


class ConnInfo(BaseConnInfo):
	async def close(self) -> None:
		return await super()._aclose()


class Monitor(BaseMonitor):
	pool: ReferenceType["PySQLXEnginePool"]

	async def run(self) -> None:
		pool = self.pool()
		logger.info("Monitor: Started monitoring the pool.")
		await pool._monitor_semaphore.acquire()
		try:
			async with pool._monitor_lock:
				conns_to_check = min(pool._pool.qsize(), pool._batch_size)
				for _ in range(conns_to_check):
					try:
						conn = pool._pool.get_nowait()
					except asyncio.QueueEmpty:
						break

					if conn.healthy is False or conn.reusable is False:
						logger.debug(f"Connection: {conn} is unhealthy, closing.")
						await pool._del_conn_unchecked(conn=conn)

					elif monotonic() >= conn.expires_at:
						logger.debug(f"Monitor: Connection {conn} has expired, renewing.")
						conn.renew_expire_at()
						await pool._put_conn_unchecked(conn)

					else:
						logger.debug(f"Monitor: Reusing healthy connection {conn}.")
						await pool._pool.put(conn)
		finally:
			# Ensure that semaphore is released even if an error occurs
			pool._monitor_semaphore.release()

		logger.debug(f"Monitor: Sleeping for {pool._check_interval} seconds.")
		await asleep(pool._check_interval)


class PySQLXEnginePool(BasePool):
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
		try:
			conn = PySQLXEngine(uri=self.uri)
			await conn.connect()
			conn_info = ConnInfo(conn=conn, keep_alive=self._keep_alive)
			logger.debug(f"Pool: New connection created: {conn_info}")
			self._size += 1
			return conn_info
		except Exception as e:
			logger.error(f"Pool: Failed to create a new connection: {e}")
			raise

	async def _del_conn_unchecked(self, conn: ConnInfo) -> None:
		try:
			await conn.close()
			self._size -= 1
			logger.debug(f"Pool: Connection closed: {conn}")
		except Exception as e:
			logger.error(f"Pool: Error closing connection {conn}: {e}")

	async def _put_conn_unchecked(self, conn: ConnInfo) -> None:
		if conn.healthy and monotonic() < conn.expires_at:
			try:
				await self._pool.put(conn)
				logger.debug(f"Pool: Connection returned to pool: {conn}")
			except asyncio.QueueFull:
				logger.debug(f"Pool: Pool is full. Closing connection: {conn}")
				await self._del_conn_unchecked(conn)
		else:
			logger.debug(f"Pool: Connection is not reusable or expired: {conn}")
			await self._del_conn_unchecked(conn)
			logger.debug("Pool: Creating a new connection to maintain pool size.")
			new_conn = await self._new_conn_unchecked()
			await self._pool.put(new_conn)

	async def _get_ready_conn(self) -> BaseConnInfo:
		if self._pool:
			logger.debug("Getting for a ready connection.")
			try:
				conn = await asyncio.wait_for(self._pool.get(), timeout=0.1)
				return conn
			except asyncio.TimeoutError:
				...

		if self._size < self._max_size:
			logger.debug("Creating a new connection.")
			conn = await self._new_conn_unchecked()
			return conn

	async def _get_conn(self) -> ConnInfo:
		self._check_closed()
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
			while True:
				timeout = deadline - monotonic()

				if timeout < 0.0:
					raise PoolTimeoutError("Timeout waiting for a connection")

				conn = await self._get_ready_conn()
				if conn:
					return conn

				await asleep(0.1)
		finally:
			self._semaphore.release()

	async def _put_conn(self, conn: ConnInfo) -> None:
		try:
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
		if self._opened and self._size > 0:
			logger.debug("Pool: Workers already started.")
			return

		await self._start()
		# Initialize and start the monitor
		self._monitor = aspawn_loop(Monitor(pool=ref(self)).run, name="ConnectionMonitor")
		self._workers.append(Worker(self._monitor))
		logger.info("Pool: Workers started.")

	async def start(self) -> None:
		await self._start_workers()

	@asynccontextmanager
	async def connection(self):
		conn = await self._get_conn()
		try:
			yield conn.conn
		except Exception as e:
			logger.error(f"Pool: Error during connection usage: {e}")
			conn.healthy = False
			raise
		finally:
			await self._put_conn(conn)

	async def _stop(self) -> None:
		if not self._opened:
			logger.debug("Pool: Attempted to stop a pool that is not opened.")
			return

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
		async with self._lock:
			await self._stop()

	async def __aenter__(self):
		await self.start()
		return self

	async def __aexit__(self, exc_type, exc, tb):
		await self.stop()
