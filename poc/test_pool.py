import asyncio
import threading
from weakref import ReferenceType, ref

from .base import BaseMonitor, BasePool, ConnInfo
from .errors import PoolClosed, PoolTimeout


def current_thread_name() -> str:
	return threading.current_thread().name


def current_task_name() -> str:
	t = asyncio.current_task()
	return t.get_name() if t else "<no task>"


class Monitor(BaseMonitor):
	def __init__(self, pool: BasePool):
		super().__init__(pool)
		self._lock = asyncio.Lock()

	def current_t_name(self) -> str:
		return current_task_name()

	async def _run(self: BaseMonitor) -> None:
		while True:
			async with self._lock:
				pool = self.pool()
				if pool._pool:
					...

			await asyncio.sleep(pool._check_interval)


class MonitorSync(BaseMonitor): ...
