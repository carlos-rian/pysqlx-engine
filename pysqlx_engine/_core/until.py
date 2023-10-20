import asyncio
import functools
import logging
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from typing import Callable, List, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel
from pysqlx_core import PySQLXError as _PySQLXError
from typing_extensions import ParamSpec

from .const import ISOLATION_LEVEL, LOG_CONFIG, PYDANTIC_IS_V1
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
from .helper import (
    fe_sql,
    isolation_error_message,
    parameters_type_error_message,
    sql_type_error_message,
)
from .param import convert

if PYDANTIC_IS_V1:
    from pydantic import parse_obj_as as _parse_obj_as  # pragma: no cover
else:
    from pydantic import TypeAdapter  # pragma: no cover


P = ParamSpec("P")
T = TypeVar("T")


def force_sync(fn: Callable[P, T]) -> Callable[P, T]:
    """
    turn an async function to sync function
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
        res = fn(*args, **kwds)
        loop = asyncio.get_event_loop()

        # if loop is already running, we don't need to run it again
        if loop.is_running():
            return res
        # if the result is a coroutine, we need to run it in the loop synchronously
        elif asyncio.iscoroutine(res):
            return loop.run_until_complete(res)

        # case the result is not a coroutine, we just return it
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
        _types = (bool, str, int, list, dict, tuple, UUID, time, date, datetime, float, bytes, Decimal, Enum)
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
        load_parameter = {key: convert(provider=provider, value=value, field=key) for key, value in parameters.items()}

        param_as_list_of_tuples = sorted(load_parameter.items(), key=lambda x: x[0], reverse=True)

        for key, value in param_as_list_of_tuples:
            new_sql = new_sql.replace(f":{key}", str(value))

    if LOG_CONFIG.PYSQLX_SQL_LOG:
        new_sql = new_sql.strip()
        logging.info(fe_sql(sql=new_sql))

    return new_sql


def parse_obj_as(type_: Union[BaseModel, List[BaseModel]], obj: Union[dict, list]) -> type:
    return _parse_obj_as(type_=type_, obj=obj) if PYDANTIC_IS_V1 else TypeAdapter(type=type_).validate_python(obj)
