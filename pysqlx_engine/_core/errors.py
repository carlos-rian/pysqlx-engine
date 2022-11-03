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

from os import getenv

from pysqlx_core import PySQLXError as _PySQLXError

from .helper import fe_json


class PySQLXError(Exception):
    def __init__(self, err: _PySQLXError, *args: object):
        self.code: str = err.code()
        self.message: str = err.message()
        self._type: str = err.error()

        msg = f"{self._type}(code={self.code}, message={self.message})"

        if getenv("PYSQLX_ERROR_JSON_FMT", "1") == "1":
            msg = fe_json(
                {
                    "code": self.code,
                    "message": self.message,
                    "error": self._type,
                }
            )

        super().__init__(msg)


class QueryError(PySQLXError):
    ...


class ExecuteError(PySQLXError):
    ...


class ConnectError(PySQLXError):
    ...


class IsoLevelError(PySQLXError):
    ...


class StartTransactionError(PySQLXError):
    ...


class RawCmdError(PySQLXError):
    ...


class NotConnectedError(Exception):
    ...


class AlreadyConnectedError(ValueError):
    ...


class NotConnectedError(ValueError):
    ...
