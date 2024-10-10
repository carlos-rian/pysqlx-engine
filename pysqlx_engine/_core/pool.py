import queue
from contextlib import contextmanager
from threading import Lock, Semaphore
from time import monotonic

from pysqlx_engine import PySQLXEngineSync as PySQLXEngine

from .abc.base_pool import BaseConnInfo, BaseMonitor, BasePool, Worker, logger
from .errors import PoolAlreadyClosedError, PoolAlreadyStartedError, PoolTimeoutError
from .util import gather, sleep, spawn

__all__ = ["PySQLXEnginePoolSync"]


class ConnInfo(BaseConnInfo):
	conn: PySQLXEngine

	def close(self) -> None:
		super()._close()


class Monitor(BaseMonitor):
	pool: "PySQLXEnginePoolSync"

	def run(self) -> None:
		logger.info("Monitor: Started monitoring the pool.")
		while self.pool._opened:
			self._checking = True
			with self.pool._monitor_lock:
				self.pool._monitor_semaphore.acquire()
				try:
					conns_to_check = min(self.pool._pool.qsize(), self.pool._batch_size)
					for _ in range(conns_to_check):
						try:
							conn = self.pool._pool.get_nowait()
						except queue.Empty:
							break

						if self.pool._size > self.pool._max_size:
							logger.debug("Monitor: Pool size is above minimum, closing connection.")
							self.pool._del_conn_unchecked(conn=conn)

						elif conn.healthy is False or conn.reusable is False:
							logger.debug(f"Connection: {conn} is unhealthy, closing.")
							self.pool._del_conn_unchecked(conn=conn)

						elif monotonic() >= conn.expires_at:
							logger.debug(f"Monitor: Connection {conn} has expired, renewing.")
							conn.renew_expires_at()
							self.pool._pool.put_nowait(conn)

						else:
							logger.debug(f"Monitor: Reusing healthy connection {conn}.")
							self.pool._pool.put_nowait(conn)

					if self.pool._size < self.pool._min_size:
						logger.debug("Monitor: Pool size is below minimum, creating new connections.")
						new_conns = gather(
							*[self.pool._new_conn_unchecked for _ in range(self.pool._min_size - self.pool._size)]
						)
						for conn in new_conns:
							self.pool._put_conn_unchecked(conn)

					elif self.pool._growing and self.pool._size < self.pool._max_size:
						logger.debug("Monitor: Pool is growing, creating new connections.")
						conn = self.pool._new_conn_unchecked()
						self.pool._put_conn_unchecked(conn)
						self.pool._growing = False

				finally:
					# Ensure that semaphore is released even if an error occurs
					self.pool._monitor_semaphore.release()

			self._checking = False
			logger.debug(f"Monitor: Sleeping for {self.pool._check_interval} seconds.")
			sleep(self.pool._check_interval)

		logger.info("Monitor: Stopped monitoring the pool.")


class PySQLXEnginePoolSync(BasePool):
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
		self._pool: queue.Queue[ConnInfo] = queue.Queue(maxsize=self._max_size)
		self._semaphore: Semaphore = Semaphore(self._max_size)
		self._monitor_lock: Lock = Lock()
		self._monitor_semaphore: Semaphore = Semaphore(1)
		self._workers: list[Worker] = []
		self._opened: bool = False
		self._opening: bool = False
		self._monitor = None
		self._batch_size = monitor_batch_size
		self._lock = Lock()

	def _new_conn_unchecked(self) -> ConnInfo:
		conn = PySQLXEngine(uri=self.uri)
		conn.connect()
		conn_info = ConnInfo(conn=conn, keep_alive=self._keep_alive)
		self._size += 1
		logger.debug(f"Pool: New connection created: {conn_info} PoolSize: {self._size}")
		return conn_info

	def _del_conn_unchecked(self, conn: ConnInfo, use_lock: bool = False) -> None:
		if use_lock:
			with self._lock:
				conn.close()
				self._size -= 1
		else:
			conn.close()
			self._size -= 1
		logger.debug(f"Pool: Connection closed: {conn} PoolSize: {self._size}")

	def _put_conn_unchecked(self, conn: ConnInfo) -> None:
		if conn.healthy and conn.reusable and self._size <= self._max_size:
			try:
				self._pool.put(conn, timeout=1)
				logger.debug(f"Pool: Connection returned to pool: {conn}")
			except queue.Full:
				logger.debug(f"Pool: Pool is full. Closing connection: {conn}")
				self._del_conn_unchecked(conn)
		else:
			logger.debug(f"Pool: Connection is not reusable or expired: {conn}")
			self._del_conn_unchecked(conn)

	def _get_ready_conn(self) -> BaseConnInfo:
		try:
			conn = self._pool.get(timeout=BaseConnInfo._jitter(value=0.3))
			return conn
		except queue.Empty:
			return

	def _check_grow(self, value: int) -> None:
		with self._lock:
			self._waiting += value
			if self._size >= self._max_size:
				return

			self._growing = self._waiting > 1
			logger.debug(f"Pool: Growing: {self._growing} Waiting: {self._waiting}")

	def _get_conn(self) -> ConnInfo:
		self._check_closed()
		start_time = monotonic()
		deadline = monotonic() + self._conn_timeout
		logger.debug("Getting a ready connection.")
		try:
			start = monotonic()
			acquired = self._semaphore.acquire(timeout=self._conn_timeout)
			if not acquired:
				raise PoolTimeoutError("Timeout waiting for a connection semaphore")
			deadline -= monotonic() - start  # Adjust deadline for time spent waiting for semaphore
			logger.debug(f"Acquired semaphore in {monotonic() - start:.5f} seconds")
		except Exception as e:
			raise PoolTimeoutError("Timeout waiting for a connection semaphore") from e

		try:
			self._check_grow(1)
			while True:
				timeout = deadline - monotonic()
				if timeout < 0.0:
					raise PoolTimeoutError("Timeout waiting for a connection")

				conn = self._get_ready_conn()
				if conn:
					logger.debug(f"Pool: Connection: {conn} retrieved in {monotonic() - start_time:.5f} seconds.")
					return conn

				sleep(BaseConnInfo._jitter(value=0.3))
		finally:
			self._check_grow(-1)
			self._semaphore.release()

	def _put_conn(self, conn: ConnInfo) -> None:
		try:
			with self._lock:
				self._put_conn_unchecked(conn)
		finally:
			self._semaphore.release()

	def _start(self) -> None:
		if self._size > 0 and self._opened:
			logger.error("Pool: Attempted to start an already opened pool.")
			raise PoolAlreadyStartedError("Pool is already started")

		self._opening = True
		logger.info("Pool: Starting the connection pool.")
		with self._lock:
			tasks = [self._new_conn_unchecked for _ in range(self._min_size)]
			try:
				conns = gather(*tasks)
				for conn in conns:
					self._pool.put(conn)
			except Exception as e:
				logger.error(f"Pool: Error during pool initialization: {e}")
				raise
			self._opened = True
			logger.info(f"Pool: Initialized with {self._min_size} connections.")
		self._opening = False

	def _start_workers(self) -> None:
		self._start()
		# Initialize and start the monitor
		self._monitor = spawn(Monitor(pool=self).run, name="ConnectionMonitor")
		self._workers.append(Worker(self._monitor))
		logger.info("Pool: Workers started.")

	def start(self) -> None:
		"""Start the pool and create the initial connections."""
		self._start_workers()

	@contextmanager
	def connection(self):
		"""
		A context manager that provides a connection from the pool.

		Use this context manager to get a connection from the pool.

		"""
		conn = self._get_conn()
		try:
			yield conn.conn
		except Exception as e:
			logger.error(f"Pool: Error during connection usage: {e}")
			raise
		finally:
			if conn.conn._on_transaction:
				logger.warning("Transaction is still active, please commit or rollback before closing the connection.")
				self._del_conn_unchecked(conn, use_lock=True)
			else:
				self._put_conn(conn)

	def _stop(self) -> None:
		if not self._opened:
			raise PoolAlreadyClosedError("Pool is already closed")

		logger.info("Pool: Stopping the connection pool.")
		self._opened = False

		# Close all connections
		while not self._pool.empty():
			conn = self._pool.get()
			self._del_conn_unchecked(conn)

		# Stop all workers
		for worker in self._workers:
			worker.finish()
		self._workers.clear()
		logger.info("Pool: All workers stopped and connections closed.")

	def stop(self) -> None:
		"""Stop the pool and close all connections."""
		with self._lock:
			self._stop()
