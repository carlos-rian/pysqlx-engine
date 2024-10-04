import asyncio
import threading
from typing import Callable

from pysqlx_engine._core.logger import logger


class PySQLXTaskSync(threading.Thread):
	"""
	A subclass of threading.Thread that sets the thread as a daemon thread.

	Where the thread will run the target function until the stop method is called.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._stop_event = threading.Event()

	def run(self):
		logger.debug(f"Starting thread: {self.name}")
		if self._target and not self._stop_event.is_set():
			logger.debug(f"Running thread: {self.name}")
			if self._target:
				self._target(*self._args, **self._kwargs)

		logger.debug(f"Stopped thread: {self.name}")

	def stop(self):
		logger.debug(f"Stopping thread: {self.name}")
		self._stop_event.set()


class PySQLXTask:
	"""
	A class that wraps a coroutine and runs it as a task.

	Where the task will run the coroutine until the stop method is called.
	"""

	def __init__(self, f: Callable, force_sleep: bool = False, name: str = None, *args, **kwargs):
		assert asyncio.iscoroutinefunction(f), f"The function must be a coroutine function. Not a {type(f).__name__}"
		self._coro = f
		self._args = args
		self._kwargs = kwargs
		self._stop_event = asyncio.Event()
		self._force_sleep = force_sleep

		self.task = asyncio.create_task(self.run(), name=name)

	@property
	def name(self):
		return self.task.get_name()

	async def run(self):
		logger.debug(f"Async -> Starting task: {self.name}")
		if self._coro and not self._stop_event.is_set():
			logger.debug(f"Async -> Running task: {self.name}")
			await self._coro(*self._args, **self._kwargs)
			if self._force_sleep:
				await asyncio.sleep(0.01)  # case the coroutine doesn't have a I/O operation

		if not self.task.done():
			self.task.cancel()

		logger.debug(f"Async -> Stopping task: {self.name}")

	def stop(self):
		self._stop_event.set()
