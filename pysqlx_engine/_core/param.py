from datetime import date, datetime, time
from decimal import Decimal
from json import dumps, loads, JSONEncoder
from typing import Union, Dict, List, Any, Tuple, Type, Callable
from uuid import UUID
from functools import lru_cache

from .const import PROVIDER
from .errors import ParameterInvalidProviderError, ParameterInvalidValueError


@lru_cache(maxsize=None)
def try_bool(provider: PROVIDER, value: bool, _f: str = "") -> str:
    if provider == "sqlserver":
        return "1" if value else "0"
    return str(value).upper()


@lru_cache(maxsize=None)
def try_str(_p: PROVIDER, value: str, _f: str = "") -> str:
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_int(_p: PROVIDER, value: int, _f: str = "") -> str:
    return f"{value}"


def try_json(provider: PROVIDER, value: Union[Dict[str, Any], List[Dict[str, Any]]], field: str = "") -> str:
    try:
        return f"'{dumps(value, ensure_ascii=False, default=str)}'"
    except Exception as err:
        raise ParameterInvalidValueError(
            field=field, provider=provider, typ_from="dict|list", typ_to="json", details=str(err)
        )


@lru_cache(maxsize=None)
def try_uuid(_a: PROVIDER, value: UUID, _f: str = "") -> str:
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_time(_p: PROVIDER, value: time, _f: str = "") -> str:
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_date(_p: PROVIDER, value: date, _f: str = "") -> str:
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_datetime(_p: PROVIDER, value: datetime, _f: str = "") -> str:
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_float(_p: PROVIDER, value: float, _f: str = "") -> str:
    return f"{value}"


@lru_cache(maxsize=None)
def try_bytes(provider: PROVIDER, value: bytes, field: str = "") -> str:
    if provider == "sqlserver":
        return f"0x{value.hex()}"

    elif provider == "postgresql":
        return f"'\\x{value.hex()}'"

    elif provider == "mysql":
        return f"X'{value.hex()}'"

    elif provider == "sqlite":
        return f"x'{value.hex()}'"

    raise ParameterInvalidProviderError(field=field, provider=provider, typ="bytes")


@lru_cache(maxsize=None)
def try_decimal(provider: PROVIDER, value: Decimal, field: str = "") -> str:
    try:
        return f"'{str(value)}'"
    except Exception as err:
        raise ParameterInvalidValueError(
            field=field, provider=provider, typ_to="decimal", typ_from="str", details=str(err)
        )


@lru_cache(maxsize=None)
def try_tuple(provider: PROVIDER, values: Tuple[Any], field: str = "") -> str:
    try:
        types = set([type(v) for v in values])

        if len(types) > 1:
            raise ParameterInvalidValueError(
                field=field,
                provider=provider,
                typ_from="tuple",
                typ_to="sql array",
                details="the tuple must be of the same type, eg: (1, 2, 3). tuple is represented as a array in sql, sql does not support heterogeneous tuple.",
            )
        if len(values) > 0:
            method = get_method(typ=types.pop())
            data = str([method(v) for v in values]).replace("[", "{").replace("]", "}")
            return f"'{data}'"
        return "'{}'"

    except Exception as err:
        raise ParameterInvalidValueError(field=field, provider=provider, typ="list", typ_from="str", details=str(err))


def get_method(typ: Type) -> Callable:
    METHODS = {
        bool: try_bool,
        str: try_str,
        int: try_int,
        list: try_json,
        dict: try_json,
        tuple: try_tuple,
        UUID: try_uuid,
        time: try_time,
        date: try_date,
        datetime: try_datetime,
        float: try_float,
        bytes: try_bytes,
        Decimal: try_decimal,
    }

    return METHODS.get(typ, try_str)


def convert(
    provider: PROVIDER,
    value: Union[
        bool, str, int, Dict[str, Any], List[Dict[str, Any]], UUID, time, date, datetime, float, bytes, Decimal, None
    ],
    field: str = "",
) -> str:
    if value is None:
        return "NULL"

    typ_ = type(value)

    method = get_method(typ=typ_)
    if method is None:
        raise ParameterInvalidProviderError(field=field, provider=provider, typ=typ_)

    return method(provider, value, field)
