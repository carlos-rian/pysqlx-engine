import functools
import asyncio

from pysqlx_core import PySQLXError as _PySQLXError

from .param import convert

from .const import ISOLATION_LEVEL, CONFIG
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
from .helper import fe_sql, isolation_error_message, parameters_type_error_message, sql_type_error_message

from datetime import date, datetime, time
from functools import lru_cache
from decimal import Decimal
from uuid import UUID


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


def check_sql_and_parameters(sql: str, parameters: dict):
    if not isinstance(sql, str):
        raise TypeError(sql_type_error_message())

    if parameters is not None:
        _types = (bool, str, int, list, dict, tuple, UUID, time, date, datetime, float, bytes, Decimal)
        if (
            not isinstance(parameters, dict)
            or not all([isinstance(key, str) for key in parameters.keys()])
            or not all([isinstance(value, _types) or value is None for value in parameters.values()])
        ):
            raise TypeError(parameters_type_error_message())


@lru_cache(maxsize=None)
def check_isolation_level(isolation_level: ISOLATION_LEVEL):
    levels = ["ReadUncommitted", "ReadCommitted", "RepeatableRead", "Snapshot", "Serializable"]
    if not isinstance(isolation_level, str) or not any([isolation_level == level for level in levels]):
        raise ValueError(isolation_error_message())


def build_sql(provider: str, sql: str, parameters: dict = None) -> str:
    new_sql = sql
    if parameters is not None:
        load_parameter = {}
        for key, value in parameters.items():
            load_parameter[key] = convert(provider=provider, value=value, field=key)

        for key, value in load_parameter.items():
            new_sql = new_sql.replace(f":{key}", f"{value}")

        if CONFIG.PYSQLX_SQL_LOG:
            print(fe_sql(sql=new_sql), flush=True)

    return new_sql
