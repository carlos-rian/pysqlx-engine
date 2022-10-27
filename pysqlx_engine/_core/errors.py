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


class NotConnectedError(Exception):
    ...


if __name__ == "__main__":

    class _X:
        def __init__(self):
            ...

        def code(self):
            return "CFRE"

        def message(self):
            return "MEHHT"

        def error(self):
            return "TEST"

    raise PySQLXError(err=_X())
