import asyncio
import logging
import threading
from abc import ABC, abstractmethod
from collections import deque as Deque
from random import random
from time import monotonic
from typing import List, Union
from weakref import ReferenceType

from typing_extensions import TypeAlias

from pysqlx_engine import PySQLXEngine, PySQLXEngineSync

from .errors import PoolClosed

logger = logging.getLogger("pysqlx_engine")
TPySQLXEngineConn: TypeAlias = Union[PySQLXEngine, PySQLXEngineSync]


def get_task_name(task: Union[asyncio.Task, threading.Thread]) -> str:
	if isinstance(task, asyncio.Task):
		return task.get_name()

	return task.name


class BaseConnInfo(ABC):
	_num_conn: int = 0

	def __init__(self, conn: TPySQLXEngineConn, keep_alive: float):
		self._num_conn = BaseConnInfo._num_conn = BaseConnInfo._num_conn + 1
		self.name = f"conn-{self._num_conn}"
		self.conn = conn

		self.keep_alive = keep_alive
		self.expire_at = monotonic() + self._jitter(value=self.keep_alive, min_pc=-0.05, max_pc=0.0)
		self.start_at = monotonic()

	def __repr__(self) -> str:
		return f"<{self.__class__.__module__}.{self.__class__.__name__} {self.name!r} at 0x{id(self):x}>"

	@property
	def _can_reuse(self) -> bool:
		finish = self.start_at + (self.keep_alive * 4)
		return finish > monotonic()

	@property
	def expires(self) -> bool:
		return self.expire_at < monotonic()

	@property
	def healthy(self) -> bool:
		return self.conn.is_healthy()

	@property
	def reusable(self) -> bool:
		return self.healthy and self.conn.connected and self._can_reuse

	@abstractmethod
	def close(self) -> None: ...

	async def _aclose(self) -> None:
		await self.conn.close()
		self.expire_at = monotonic()
		print(f"Removed: {self} from pool, the conn was open for {self.expire_at - self.start_at} secs")

	def _close(self) -> None:
		self.conn.close()
		self.expire_at = monotonic()
		print(f"Removed: {self} from pool, the conn was open for {self.expire_at - self.start_at} secs")

	def renew_expire_at(self):
		self.expire_at = monotonic() + self._jitter(value=self.keep_alive, min_pc=-0.05, max_pc=0.0)

	@classmethod
	def _jitter(cls, value: float, min_pc: float, max_pc: float) -> float:
		"""
		Add a random value to *value* between *min_pc* and *max_pc* percent.
		"""
		return value * (1.0 + ((max_pc - min_pc) * random()) + min_pc)


class PySQLXEngineWorker:
	_worker_num = 0

	def __init__(self, task: Union[asyncio.Task, threading.Thread]):
		self.task = task
		self._worker_num = PySQLXEngineWorker._worker_num = PySQLXEngineWorker._worker_num + 1
		self.name = f"worker-{self._worker_num}-{get_task_name(task)}"
		logger.debug(f"Worker: {self.name} starting.")

	def finish(self):
		logger.debug(f"Worker: {self.name} finishing.")
		if isinstance(self.task, asyncio.Task):
			self.task.cancel()
		else:
			self.task.join()


class BasePool(ABC):
	_num_pool = 0

	def __init__(
		self,
		uri: str,
		min_size: int,
		max_size: int = None,
		conn_timeout: float = 30.0,
		keep_alive: float = 60 * 15,
		check_interval: float = 2.0,
	):
		"""
		:param uri: The connection URI.
		:param min_size: The minimum connections in the pool.
		:param max_size: The maximum connections in the pool.
		:param conn_timeout: The timeout in seconds to wait for a connection must be returned by the pool.
		:param max_lifetime: The maximum lifetime of a connection in seconds.
		:param check_interval: The interval in seconds to check for idle connections to be closed, recycled or created.
		"""
		# check if the uri is valid
		PySQLXEngine(uri)

		self.uri = uri
		self._conn_timeout = conn_timeout or 30.0
		self._keep_alive = keep_alive or 60 * 15
		self._check_interval = check_interval or 5.0

		assert self._conn_timeout > 0, "conn_timeout must be greater than 0"
		assert self._keep_alive > 0, "max_lifetime must be greater than 0"
		assert check_interval > 0, "check_interval must be greater than 0"

		if self._keep_alive < 60:
			logger.warning("max_lifetime is less than 60 seconds, this is not recommended")

		self._num_pool = BasePool._num_pool = BasePool._num_pool + 1
		self._name = f"{self.__class__.__name__}-{self._num_pool}"

		self._size = 0
		self._pool: Deque[BaseConnInfo] = Deque()
		self._opened = False
		self._opening = False

		self._min_size, self._max_size = self._check_size(min_size, max_size)

		self._lock: Union[asyncio.Lock, threading.RLock]

		self._workers: List[PySQLXEngineWorker] = []

	def __repr__(self) -> str:
		return f"<{self.__class__.__module__}.{self.__class__.__name__} {self._name!r} at 0x{id(self):x}>"

	@property
	def closed(self) -> bool:
		return self._opened is False

	def _check_size(self, min_size: int, max_size: Union[int | None]):
		if max_size is None:
			max_size = min_size

		if min_size <= 0:
			raise ValueError("min_size must be greater than 0")

		elif max_size < min_size:
			raise ValueError("min_size must be less than max_size")

		return min_size, max_size

	def _check_closed(self) -> None:
		if self.closed is True and self._opening is False:
			raise PoolClosed("Pool is closed")

	@abstractmethod
	def _new_conn(self) -> BaseConnInfo: ...

	@abstractmethod
	def _del_conn(self, conn: BaseConnInfo) -> None: ...

	@abstractmethod
	def _put_conn(self, conn: BaseConnInfo) -> None: ...

	@abstractmethod
	def _get_ready_conn(self) -> BaseConnInfo: ...

	@abstractmethod
	def _get_conn(self) -> BaseConnInfo: ...

	@abstractmethod
	def _start(self) -> None: ...

	@abstractmethod
	def _start_workers(self) -> None: ...

	@abstractmethod
	def get_connection(self) -> TPySQLXEngineConn: ...

	@abstractmethod
	def stop(self) -> None: ...


class BaseMonitor:
	def __init__(self, pool: ReferenceType[BasePool]):
		self.pool: ReferenceType[BasePool] = pool

	def __repr__(self) -> str:
		pool = self.pool()
		name = repr(pool._name) if pool else "<pool is gone>"
		return f"<{self.__class__.__name__} {name} at 0x{id(self):x}>"

	@abstractmethod
	def current_t_name(self) -> str:
		"""Return the current thread or task name."""
		...

	@abstractmethod
	def run(self) -> None:
		pass
