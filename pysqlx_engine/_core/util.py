import asyncio
import logging
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from datetime import time as dt_time
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Coroutine, List, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel
from pysqlx_core import PySQLxError as _PySQLXError

from .abc.workers import PySQLXTask, PySQLXTaskSync
from .const import ISOLATION_LEVEL, PYDANTIC_IS_V1
from .errors import (
	ConnectError,
	ExecuteError,
	IsoLevelError,
	NotConnectedError,
	PySQLXError,
	QueryError,
	RawCmdError,
	StartTransactionError,
)
from .helper import isolation_error_message, parameters_type_error_message, sql_type_error_message
from .param_converter import convert

if PYDANTIC_IS_V1:
	from pydantic import parse_obj_as as _parse_obj_as  # pragma: no cover
else:
	from pydantic import TypeAdapter  # pragma: no cover


def pysqlx_get_error(err: _PySQLXError) -> PySQLXError:
	types_err = {
		"ConnectError": ConnectError,
		"ExecuteError": ExecuteError,
		"NotConnectedError": NotConnectedError,
		"IsoLevelError": IsoLevelError,
		"PySQLXError": PySQLXError,
		"QueryError": QueryError,
		"RawCmdError": RawCmdError,
		"StartTransactionError": StartTransactionError,
	}
	error: PySQLXError = types_err.get(err.error())
	if error is not None:
		return error(err=err)
	return err


def check_sql_and_parameters(sql: str, parameters: dict):
	if not isinstance(sql, str):
		raise TypeError(sql_type_error_message())

	if parameters is not None:
		_types = (bool, str, int, list, dict, tuple, UUID, dt_time, date, datetime, float, bytes, Decimal, Enum)
		if (
			not isinstance(parameters, dict)
			or not all([isinstance(key, str) for key in parameters.keys()])
			or not all([isinstance(value, _types) or value is None for value in parameters.values()])
		):
			raise TypeError(parameters_type_error_message())


@lru_cache(maxsize=None)
def check_isolation_level(isolation_level: ISOLATION_LEVEL):
	levels = [
		"ReadUncommitted",
		"ReadCommitted",
		"RepeatableRead",
		"Snapshot",
		"Serializable",
	]
	if not isinstance(isolation_level, str) or not any([isolation_level == level for level in levels]):
		raise ValueError(isolation_error_message())


def build_sql(provider: str, sql: str, parameters: dict = None) -> str:
	new_sql = sql
	if parameters is not None:
		load_parameter = {key: convert(provider=provider, value=value, field=key) for key, value in parameters.items()}

		param_as_list_of_tuples = sorted(load_parameter.items(), key=lambda x: x[0], reverse=True)

		for key, value in param_as_list_of_tuples:
			new_sql = new_sql.replace(f":{key}", str(value))
	return new_sql


def parse_obj_as(type_: Union[BaseModel, List[BaseModel]], obj: Union[dict, list]) -> type:
	return _parse_obj_as(type_=type_, obj=obj) if PYDANTIC_IS_V1 else TypeAdapter(type=type_).validate_python(obj)


@lru_cache(maxsize=None)
def get_logger_length() -> int:
	try:
		logger = logging.getLogger()  # fake logger, just to get the prefix length
		test_record = logger.makeRecord(
			name=logger.name, level=logger.level, fn="", lno=0, msg="", args=(), exc_info=None
		)
		prefix = logger.handlers[0].format(test_record)
		return len(prefix)
	except Exception:  # pragma: no cover
		return 0  # pragma: no cover


def create_log_line(text: str, character: str = "=") -> str:
	# Get the terminal width
	terminal_width = shutil.get_terminal_size().columns
	logger_lenght = get_logger_length()
	terminal_width -= logger_lenght if terminal_width > logger_lenght else 0

	# If the text is longer than the terminal width, truncate it
	if len(text) > terminal_width:
		text = text[:terminal_width]

	# Calculate the space needed to center the text
	space = (terminal_width - len(text)) // 2

	# Create the line
	line = f"{character * space}{text}{character * space}"

	# If there's any difference, adjust the line to match the terminal width
	if len(line) < terminal_width:
		line += character * (terminal_width - len(line))  # pragma: no cover

	return line


T = TypeVar("T")


def aspawn(f: Callable, args: tuple = (), name: Union[str, None] = None) -> PySQLXTask:
	"""
	Equivalent to asyncio.create_task.

	Where the task will run the coroutine until the stop method is called.
	"""
	t = PySQLXTask(f=f, name=name, *args)
	return t


def spawn(f: Callable, args: tuple = (), name: Union[str, None] = None) -> PySQLXTaskSync:
	"""
	Equivalent to creating and running a daemon thread.

	Where the thread will run the target function until the stop method is called.
	"""
	t = PySQLXTaskSync(target=f, args=args, name=name, daemon=True)
	t.start()
	return t


def sleep(seconds: float) -> None:
	"""
	Equivalent to time.sleep().
	"""
	return time.sleep(seconds)


def asleep(seconds: float) -> Coroutine[Any, Any, None]:
	"""
	Equivalent to asyncio.sleep(), converted to time.sleep() by async_to_sync.
	"""
	return asyncio.sleep(seconds)


async def agather(*coro: Coroutine):
	"""
	Equivalent to asyncio.gather().
	"""
	return await asyncio.gather(*coro)


def gather(*funcs: Callable, **kwargs):
	"""
	Equivalent to threading.Thread(target=func).start().
	"""
	max_workers = min(32, (os.cpu_count() or 1) + 2)
	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [executor.submit(func, **kwargs) for func in funcs]
		results = [future.result() for future in as_completed(futures)]

	return results


def monotonic():
	"""
	Equivalent to time.monotonic().
	"""
	return time.monotonic()
