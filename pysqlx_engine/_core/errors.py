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
    """Base class for all PySQLXEngine errors."""

    def __init__(self, err: _PySQLXError, *args: object):
        self.code: str = err.code()
        self.message: str = err.message()
        self._type: str = err.error()

        if getenv("PYSQLX_ERROR_JSON_FMT", "0") == "1":
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

    def code(self) -> str:
        """Return the error code."""
        return self.code

    def message(self) -> str:
        """Return the error message."""
        return self.message

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
        if getenv("PYSQLX_ERROR_JSON_FMT", "0") == "1":
            msg = fe_json(
                {
                    "code": "0",
                    "message": "Already connected to the database",
                    "error": "AlreadyConnectedError",
                }
            )

            super().__init__(msg)
        else:
            msg = f"AlreadyConnectedError(code=0, message='Already connected to the database')"
            super().__init__(msg)
