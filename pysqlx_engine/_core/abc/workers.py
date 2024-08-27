import asyncio
import logging
import threading
from typing import Callable

from pysqlx_engine._core.logger import logger

logging.basicConfig(level=logging.DEBUG)


class PySQLXThread(threading.Thread):
	"""
	A subclass of threading.Thread that sets the thread as a daemon thread.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._stop_event = threading.Event()

	def run(self):
		logger.debug(f"Starting thread: {self.name}")
		while not self._stop_event.is_set():
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
		while not self._stop_event.is_set():
			logger.debug(f"Async -> Running task: {self.name}")
			if self._coro:
				await self._coro(*self._args, **self._kwargs)
				if self._force_sleep:
					await asyncio.sleep(0.01)  # case the coroutine doesn't have a I/O operation

		self.task.cancel()
		logger.debug(f"Async -> Stopped task: {self.name}")

	def stop(self):
		logger.debug(f"Async -> Stopping task: {self.name}")
		self._stop_event.set()


if __name__ == "__main__":

	async def main():
		async def my_function():
			print("Hello from external function!")
			await asyncio.sleep(0.5)

		# create a task
		task = PySQLXTask(my_function)

		# await the task
		await asyncio.sleep(5)

		# create a event to stop the task
		task.stop()

		# await the task
		await asyncio.sleep(1)

	asyncio.run(main())
