from datetime import date, datetime, time
from decimal import Decimal
import json
from typing import Union, Dict, List, Any, Tuple, Type, Callable
from uuid import UUID
from functools import lru_cache

from .const import PROVIDER
from .errors import ParameterInvalidJsonValueError, ParameterInvalidProviderError, ParameterInvalidValueError


@lru_cache(maxsize=None)
def try_bool(provider: PROVIDER, value: bool, _f: str = "") -> str:
    if provider.startswith("sqlserver") or provider.startswith("mysql"):
        return "1" if value else "0"
    return str(value).upper()


@lru_cache(maxsize=None)
def try_str(provider: PROVIDER, value: str, _f: str = "") -> str:
    if provider == "sqlserver":
        value = value.replace("'", "''")
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_int(_p: PROVIDER, value: int, _f: str = "") -> int:
    return value


def try_json(provider: PROVIDER, value: Union[Dict[str, Any], List[Dict[str, Any]]], _f: str = "") -> str:
    data = json.dumps(value, ensure_ascii=False, cls=PySQLXJsonEnconder)
    if provider == "sqlserver":
        data = data.replace("'", "''")
    return f"'{data}'"


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
def try_datetime(provider: PROVIDER, value: datetime, _f: str = "") -> str:
    if provider == "sqlserver":
        f"'{value.isoformat(timespec='milliseconds')}'"
    return f"'{value}'"


@lru_cache(maxsize=None)
def try_float(_p: PROVIDER, value: float, _f: str = "") -> float:
    return value


@lru_cache(maxsize=None)
def try_bytes(provider: PROVIDER, value: bytes, field: str = "") -> str:
    if provider == "sqlserver":
        return f"0x{value.hex()}"

    elif provider == "postgresql":
        return f"'\\x{value.hex()}'"

    elif provider == "mysql":
        return f"X'{value.hex()}'"

    # sqlite
    return f"x'{value.hex()}'"


@lru_cache(maxsize=None)
def try_decimal(_p: PROVIDER, value: Decimal, _f: str = "") -> str:
    return f"'{str(value)}'"


@lru_cache(maxsize=None)
def try_tuple(provider: PROVIDER, values: Tuple[Any], field: str = "") -> str:
    if not provider.startswith("postgresql"):
        raise ParameterInvalidProviderError(field=field, provider=provider, typ="array")

    types = set([type(v) for v in values])

    if len(types) > 1:
        raise ParameterInvalidValueError(
            field=field,
            provider=provider,
            typ_from="tuple",
            typ_to="array",
            details=(
                "the tuple must be of the same type, eg: (1, 2, 3). "
                "tuple is represented as a array in sql, sql does not support heterogeneous array."
            ),
        )

    if len(values) > 0:
        typ_ = types.pop()
        method = get_method(typ=typ_)

        if method is None:
            raise ParameterInvalidProviderError(field=field, provider=provider, typ=typ_)

        data = str([method(provider, value, field) for value in values]).replace("[", "{").replace("]", "}")
        return f"'{data}'"
    return "'{}'"


class PySQLXJsonEnconder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()

        elif isinstance(obj, (UUID, time, date, datetime, Decimal)):
            return str(obj)

        try:
            return super().default(obj)
        except TypeError as err:
            raise ParameterInvalidJsonValueError(
                typ_from=type(obj),
                typ_to="json",
                details=str(err),
            )


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

    return METHODS.get(typ)


def convert(
    provider: PROVIDER,
    value: Union[
        bool, str, int, Dict[str, Any], List[Dict[str, Any]], UUID, time, date, datetime, float, bytes, Decimal, None
    ],
    field: str = "",
) -> Union[str, int, float]:
    if value is None:
        return "NULL"

    typ_ = type(value)

    method = get_method(typ=typ_)
    if method is None:
        raise ParameterInvalidValueError(
            field=field,
            provider=provider,
            typ_from=typ_,
            typ_to="str|int|float",
            details="invalid type, the value is not a allowed type.",
        )

    return method(provider, value, field)
