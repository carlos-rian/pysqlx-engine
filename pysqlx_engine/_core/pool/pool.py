import threading
from contextlib import contextmanager
from time import monotonic
from weakref import ReferenceType, ref

from pysqlx_engine import PySQLXEngineSync

from ..abc.base_pool import BaseConnInfo, BaseMonitor, BasePool, Worker, logger
from ..errors import PoolAlreadyStarted, PoolTimeout
from ..util import sleep, spawn_loop


### Sync Pool
class ConnInfoSync(BaseConnInfo):
	def close(self) -> None:
		return super()._close()


class MonitorSync(BaseMonitor):
	pool: ReferenceType["PySQLXEnginePoolSync"]

	def __init__(self, pool: ReferenceType["PySQLXEnginePoolSync"]):
		self.pool = pool

	def run(self) -> None:
		pool = self.pool()
		if pool._opened and pool._size > 0 and not pool._lock.locked():
			with pool._lock:
				for _ in range(len(pool._pool)):
					conn = pool._pool.popleft()
					if conn.healthy is False:
						logger.debug(f"Connection: {conn} is unhealthy, closing.")
						pool._del_conn(conn=conn)

					elif (pool._min_size > pool._size < pool._max_size) or pool._size > pool._max_size:
						# close the connection
						logger.debug(f"Connection: {conn} health, but pool is full, closing.")
						pool._del_conn(conn=conn)

					elif conn.expires:
						# reuse the connection
						logger.debug(f"Connection: {conn} health, renewing.")
						conn.renew_expire_at()
						pool._put_conn_unchecked(conn=conn)

					else:
						# reuse the connection
						logger.debug(f"Connection: {conn} health, reusing.")
						pool._put_conn_unchecked(conn=conn)
		else:
			logger.debug("Pool is closed, waiting for the next check.")

		logger.debug(f"Sleeping for {pool._check_interval} seconds")
		sleep(pool._check_interval)


class PySQLXEnginePoolSync(BasePool):
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
		self._lock: threading.Lock = threading.Lock()

	def __del__(self) -> None:
		if self._opened:
			self._stop()

	def _new_conn(self) -> ConnInfoSync:
		conn = PySQLXEngineSync(uri=self.uri)
		conn.connect()
		conn_info = ConnInfoSync(conn=conn, keep_alive=self._keep_alive)
		logger.debug(f"Connection: {conn_info} created.")
		return conn_info

	def _del_conn(self, conn: ConnInfoSync) -> None:
		logger.debug(f"Connection: {conn} closing.")
		conn.close()
		self._size -= 1

	def _put_conn(self, conn: ConnInfoSync) -> None:
		self._check_closed()
		if not conn.reusable:
			logger.debug(f"Connection: {conn} is not reusable, closing.")
			self._del_conn(conn)
			logger.debug("Creating a new connection.")
			conn = self._new_conn()

		self._pool.append(conn)
		self._size += 1

	def _put_conn_unchecked(self, conn: BaseConnInfo) -> None:
		self._check_closed()
		if not conn.reusable:
			logger.debug(f"Connection: {conn} is not reusable, closing.")
			self._del_conn(conn)
			logger.debug("Creating a new connection.")
			conn = self._new_conn()

		self._pool.append(conn)

	def _get_ready_conn(self) -> ConnInfoSync:
		logger.debug("Getting a ready connection.")
		if self._pool:
			logger.debug("Getting for a ready connection.")
			conn = self._pool.popleft()
			return conn

		if self._size < self._max_size:
			logger.debug("Creating a new connection.")
			conn = self._new_conn()
			return conn

	def _get_conn(self) -> ConnInfoSync:
		self._check_closed()
		deadline = monotonic() + self._conn_timeout

		while True:
			timeout = deadline - monotonic()

			if timeout < 0.0:
				raise PoolTimeout("Timeout waiting for a connection")

			conn = self._get_ready_conn()
			if conn:
				return conn

			sleep(0.1)

	def _start(self) -> None:
		if self._size > 0 and self._opened:
			raise PoolAlreadyStarted("Pool is already started")

		self._opening = True
		logger.debug("Starting the pool.")
		with self._lock:
			for _ in range(self._min_size):
				conn = self._new_conn()
				self._put_conn(conn)
			self._opened = True

		logger.debug(f"Pool started with {self._min_size} connections.")
		self._opening = False

	def _start_workers(self) -> None:
		if self._opened and self._size > 0:
			return

		logger.debug("Starting the pool workers.")
		self._start()

		task_monitor = spawn_loop(MonitorSync(pool=ref(self)).run, name="Monitor")

		self._workers.append(Worker(task_monitor))

	def start(self) -> None:
		self._start_workers()

	@contextmanager
	def connection(self):
		conn = self._get_conn()
		try:
			yield conn.conn
		finally:
			self._put_conn(conn)

	def _stop(self) -> None:
		if not self._opened:
			return

		logger.debug("Stopping the pool.")
		self._opened = False
		self._opening = False

		if getattr(self, "_pool", None):
			while self._pool:
				conn = self._pool.popleft()
				self._del_conn(conn)

		if getattr(self, "_workers", None):
			for _ in range(len(self._workers)):
				worker = self._workers.pop()
				worker.finish()

	def stop(self) -> None:
		with self._lock:
			self._stop()
