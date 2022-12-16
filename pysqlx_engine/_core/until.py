import functools
import asyncio

from pysqlx_core import PySQLXError as _PySQLXError

from pysqlx_engine._core.errors import (
    ConnectError,
    ExecuteError,
    IsoLevelError,
    NotConnectedError,
    PySQLXError,
    QueryError,
    RawCmdError,
    StartTransactionError,
)


def force_sync(fn):
    """
    turn an async function to sync function
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return asyncio.get_event_loop().run_until_complete(res)
        return res

    return wrapper


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
