import asyncio
import threading
import time
from typing import Any, Callable, Coroutine, TypeVar, Union

T = TypeVar("T")


def aspawn(
	f: Callable[..., Coroutine[Any, Any, None]], args: tuple[Any, T] = (), name: str | None = None
) -> asyncio.Task[None]:
	"""
	Equivalent to asyncio.create_task.
	"""
	return asyncio.create_task(f(*args), name=name)


def asleep(seconds: float) -> Coroutine[Any, Any, None]:
	"""
	Equivalent to asyncio.sleep(), converted to time.sleep() by async_to_sync.
	"""
	return asyncio.sleep(seconds)


def sleep(seconds: float) -> None:
	"""
	Equivalent to time.sleep().
	"""
	return time.sleep(seconds)


def spawn(f: Callable[..., Any], args: tuple[Any, T] = (), name: str | None = None) -> threading.Thread:
	"""
	Equivalent to creating and running a daemon thread.
	"""
	t = threading.Thread(target=f, args=args, name=name, daemon=True)
	t.start()
	return t


def get_task_name(task: Union[asyncio.Task, threading.Thread]) -> str:
	if isinstance(task, asyncio.Task):
		return task.get_name()

	return task.name
