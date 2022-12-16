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
from typing import Any

from pysqlx_core import PySQLXError as _PySQLXError

from .const import (
    PROVIDER,
    CODE_AlreadyConnectedError,
    CODE_PoolMaxConnectionsError,
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

        if getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0":
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
        if getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0":
            msg = fe_json(
                {
                    "code": CODE_AlreadyConnectedError,
                    "message": "Already connected to the database",
                    "error": "AlreadyConnectedError",
                }
            )

            super().__init__(msg)
        else:
            msg = f"AlreadyConnectedError(code='{CODE_AlreadyConnectedError}', message='Already connected to the database')"
            super().__init__(msg)


class PoolMaxConnectionsError(Exception):
    """
    Raised when the user tries to get a connection from the pool
    but the maximum number of connections has been reached.
    """

    def __init__(self, *args: object) -> None:
        if getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0":
            msg = fe_json(
                {
                    "code": CODE_PoolMaxConnectionsError,
                    "message": "maximum number of connections reached",
                    "error": "PoolMaxConnectionsError",
                }
            )

            super().__init__(msg)
        else:
            msg = f"PoolMaxConnectionsError(code='{CODE_PoolMaxConnectionsError}', message='maximum number of connections reached')"
            super().__init__(msg)


class ParameterInvalidProviderError(Exception):
    """
    Raised when the user tries to pass an invalid type to a provider.
    """

    def __init__(self, field: str, provider: PROVIDER, typ: Any) -> None:
        self.field = field
        self.provider = provider
        self.type = typ

        if getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0":
            msg = fe_json(
                {
                    "code": CODE_ParameterInvalidProviderError,
                    "message": f"the pysqlx-engine for provider '{self.provider}' does not support converting, the type '{self.type}' is not supported.",
                    "error": "ParameterInvalidError",
                }
            )
            super().__init__(msg)
        else:
            msg = f"ParameterInvalidError(code='{CODE_ParameterInvalidProviderError}', message='the pysqlx-engine for provider '{self.provider}' does not support converting.')"
            super().__init__(msg)


class ParameterInvalidValueError(Exception):
    """
    Raised when the user tries to pass an invalid parameter to the sql.
    """

    def __init__(self, field: str, provider: PROVIDER, typ_from: Any, typ_to: Any, details: str) -> None:
        self.field = field
        self.provider = provider
        self.type_from = typ_from
        self.type_to = typ_to
        self.details = details

        if getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0":
            msg = fe_json(
                {
                    "code": CODE_ParameterInvalidValueError,
                    "message": f"the pysqlx-engine for provider '{self.provider}', error converting value '{self.typ_from}' to type '{self.typ_to}'.",
                    "error": "ParameterInvalidError",
                    "details": details,
                }
            )
            super().__init__(msg)
        else:
            msg = f"ParameterInvalidError(code='{CODE_ParameterInvalidValueError}', message='the pysqlx-engine for provider '{self.provider}', error converting value '{self.typ_from}' to type '{self.typ_to}'."
            super().__init__(msg)
