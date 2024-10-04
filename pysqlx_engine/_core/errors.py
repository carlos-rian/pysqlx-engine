"""
This module contains the errors that can be raised by the PySQLXEngine.

* PySQLXError
* QueryError
* ExecuteError
* ConnectError
* IsoLevelError
* StartTransactionError
* NotConnectedError

"""

from typing import Any

from pysqlx_core import PySQLxError as _PySQLXError

from .const import (
	LOG_CONFIG,
	PROVIDER,
	CODE_AlreadyConnectedError,
	CODE_ParameterInvalidJsonValueError,
	CODE_ParameterInvalidProviderError,
	CODE_ParameterInvalidValueError,
)
from .helper import fe_json


class PySQLXError(Exception):
	"""Base class for all PySQLXEngine errors."""

	def __init__(self, err: _PySQLXError, *args: object):
		self.code: str = err.code()
		self.message: str = err.message()
		self._type: str = err.error()

		if LOG_CONFIG.PYSQLX_ERROR_JSON_FMT:
			msg = fe_json(
				{
					"code": self.code,
					"message": self.message,
					"error": self._type,
				}
			)
			super().__init__(msg)
		else:
			msg = f"{self._type}(code='{self.code}', message='{self.message}')"
			super().__init__(msg)

	def error(self) -> str:
		"""Return the error type."""
		return self._type


class QueryError(PySQLXError):
	"""
	Raised when a query fails.
	"""

	...


class ExecuteError(PySQLXError):
	"""
	Raised when an error occurs while executing a query or invalid sql.
	"""

	...


class ConnectError(PySQLXError):
	"""Raised when a connection error occurs."""

	...


class IsoLevelError(PySQLXError):
	"""
	Raised when the isolation level is not supported or not valid
	"""

	...


class StartTransactionError(PySQLXError):
	"""
	Raised when the user tries to start a transaction
	while there is already an active transaction for example.
	"""

	...


class RawCmdError(PySQLXError):
	"""
	Raised when the user tries to execute a raw command

	"""

	...


class NotConnectedError(Exception):
	"""
	Raised when the user tries to execute a sql but is not connected to the database.
	"""

	...


class AlreadyConnectedError(Exception):
	"""
	Raised when the user tries to connect to the database but is already connected.
	"""

	def __init__(self, *args: object) -> None:
		if LOG_CONFIG.PYSQLX_ERROR_JSON_FMT:
			msg = fe_json(
				{
					"code": CODE_AlreadyConnectedError,
					"message": "Already connected to the database",
					"error": "AlreadyConnectedError",
				}
			)

			super().__init__(msg)
		else:
			msg = (
				f"AlreadyConnectedError(code='{CODE_AlreadyConnectedError}', "
				"message='Already connected to the database')"
			)
			super().__init__(msg)


class ParameterInvalidProviderError(Exception):
	"""
	Raised when the user tries to pass an invalid type to a provider.
	"""

	def __init__(self, field: str, provider: PROVIDER, typ: Any) -> None:
		self.field = field
		self.provider = provider
		self.type = typ

		message = f"the provider '{self.provider}' does not support the type '{self.type}'."

		if LOG_CONFIG.PYSQLX_ERROR_JSON_FMT:
			msg = fe_json(
				{
					"code": CODE_ParameterInvalidProviderError,
					"message": message,
					"error": "ParameterInvalidError",
				}
			)
			super().__init__(msg)
		else:
			msg = f"ParameterInvalidError(code='{CODE_ParameterInvalidProviderError}', " f"message='{message}')"
			super().__init__(msg)


class ParameterInvalidValueError(Exception):
	"""
	Raised when the user tries to pass an invalid parameter to the sql.
	"""

	def __init__(self, field: str, provider: PROVIDER, typ_from: Any, typ_to: Any, details: str = None) -> None:
		self.field = field
		self.provider = provider
		self.typ_from = typ_from
		self.typ_to = typ_to
		self.details = details

		message = (
			f"pysqlx-engine for the provider: {self.provider} had an error converting the type "
			f"'{self.typ_from}' to type '{self.typ_to}'. types supported: "
			"(bool, bytes, date, datetime, Decimal, dict, float, int, list, str, time, tuple, UUID, None)."
		)

		if LOG_CONFIG.PYSQLX_ERROR_JSON_FMT:
			msg = fe_json(
				{
					"code": CODE_ParameterInvalidValueError,
					"message": message,
					"error": "ParameterInvalidError",
					"details": details,
				}
			)
			super().__init__(msg)
		else:
			msg = (
				f"ParameterInvalidError(code='{CODE_ParameterInvalidValueError}', "
				f"message='{message}', details='{details}')"
			)
			super().__init__(msg)


class ParameterInvalidJsonValueError(Exception):
	"""
	Raised when the user tries to pass an invalid value parameter to convert json.
	"""

	def __init__(self, typ_from: str, typ_to: str, details: str = None) -> None:
		self.typ_from = typ_from
		self.typ_to = typ_to
		self.details = details

		message = (
			f"error to convert the type '{self.typ_from}' to json value. types supported: "
			"(bool, bytes, date, datetime, Decimal, dict, float, int, list, str, time, tuple, UUID, None)."
		)

		if LOG_CONFIG.PYSQLX_ERROR_JSON_FMT:
			msg = fe_json(
				{
					"code": CODE_ParameterInvalidJsonValueError,
					"message": message,
					"error": "ParameterInvalidError",
					"details": details,
				}
			)
			super().__init__(msg)
		else:
			msg = (
				f"ParameterInvalidError(code='{CODE_ParameterInvalidJsonValueError}', "
				f"message='{message}', details='{self.details}')"
			)
			super().__init__(msg)


# new pool
class PoolClosedError(Exception): ...


class PoolTimeoutError(Exception): ...


class PoolAlreadyStartedError(Exception): ...


class PoolAlreadyClosedError(Exception): ...
