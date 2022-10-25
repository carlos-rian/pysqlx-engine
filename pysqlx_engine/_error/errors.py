from pysqlx_core import PySQLXError as _PySQLXError

ConnectionError

class PySQLXError(Exception):
    def __init__(self, err: _PySQLXError):
        self.code: str = err.code()
        self.message: str = err.message()
        self.type: str = err.error()

    def __str__(self):
        return f"{self.type}(code={self.code}, message={self.message})"

    def __repr__(self):
        return f"{self.type}(code={self.code}, message={self.message})"

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

def pysqlx_get_error(err: PySQLXError) -> PySQLXError:
    types_err =  {
        "QueryError": QueryError,
        "ExecuteError": ExecuteError,
        "ConnectionError": ConnectError,
        "IsoLevelError": IsoLevelError,
        "StartTransactionError": StartTransactionError,
    }
    error: PySQLXError  = types_err.get(err.error())
    if error is not None:
        return error(err=error)
    return err


