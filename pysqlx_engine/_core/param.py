import json
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Dict, List, Tuple, Type, Union
from uuid import UUID

from pysqlx_engine._core.json_econder import PySQLXJsonEnconder

from .const import PROVIDER
from .errors import ParameterInvalidProviderError, ParameterInvalidValueError

SupportedValueType = Union[
	bool,
	str,
	int,
	Dict[str, Any],
	List[Dict[str, Any]],
	UUID,
	time,
	date,
	datetime,
	float,
	bytes,
	Decimal,
	Enum,
	None,
]


@lru_cache(maxsize=None)
def try_bool(provider: PROVIDER, value: bool, _f: str = "") -> str:
	if provider.startswith("sqlserver") or provider.startswith("mysql"):
		return "1" if value else "0"
	return str(value).upper()


@lru_cache(maxsize=None)
def try_str(provider: PROVIDER, value: str, _f: str = "") -> str:
	value = value.replace("'", "''")
	return f"'{value}'"


@lru_cache(maxsize=None)
def try_int(_p: PROVIDER, value: int, _f: str = "") -> int:
	return value


def try_json(provider: PROVIDER, value: Union[Dict[str, Any], List[Dict[str, Any]]], _f: str = "") -> str:
	data = json.dumps(value, ensure_ascii=False, cls=PySQLXJsonEnconder).replace("'", "''")
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
		return f"'{value.isoformat(timespec='milliseconds').split('+')[0]}'"
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
def try_enum(provider: PROVIDER, value: Enum, field: str = "") -> str:
	new_value = value.value
	func = get_method(typ=type(new_value))
	return func(provider, new_value, field)


def try_tuple_enum(provider: PROVIDER, values: List[Enum], field: str = "") -> str:
	if not provider.startswith("postgresql"):
		raise ParameterInvalidProviderError(field=field, provider=provider, typ="array")

	types = set([type(v) for v in values])

	if len(types) > 1:
		raise ParameterInvalidValueError(
			field=field,
			provider=provider,
			typ_from="list[enum]",
			typ_to="array",
			details=(
				"the list[enum] must be of the same type, eg: [Enum1, Enum2, Enum3]. "
				"list[enum] is represented as a array in sql, sql does not support heterogeneous array."
			),
		)

	data = ",".join([str(v.value) for v in values])
	return "'{" + data + "}'"


@lru_cache(maxsize=None)
def try_tuple(provider: PROVIDER, values: Tuple[Any], field: str = "") -> str:
	types = set([type(v) for v in values])
	if len(values) > 0:
		typ_ = types.pop()
		method = get_method(typ=typ_)

		data = str([method(provider, value, field) for value in values]).replace("[", "{").replace("]", "}")
		return f"'{data}'"

	return "'{}'"


def get_method(typ: Type) -> Callable:
	METHODS = {
		bool: try_bool,
		str: try_str,  # try_str, change to try_nstr
		int: try_int,
		list: try_json,  # try_json, change to try_njson
		dict: try_json,  # try_json, change to try_njson
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
